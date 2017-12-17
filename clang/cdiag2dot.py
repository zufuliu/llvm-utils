#!/usr/bin/env python
#-*- coding: UTF-8 -*-
import sys
import os
import operator
from collections import OrderedDict
import glob
import json
import subprocess
from plist import parse_plist_file

def has_any(collection, items):
	return any(item for item in collection if item in items)

CEscapeSequence = {
	'\"': r'\0',
	'\n': r'\n',
	'\r': r'\r',
	'\t': r'\t',
	'\\': r'\\',
	'\a': r'\a',
	'\b': r'\b',
	'\v': r'\v',
	'\f': r'\f',
	'\0': r'\0'
}

def escape_cstr(s):
	if not s or not has_any(s, ('\"\n\r\t\\\a\b\v\f\0')):
		return s

	buf = []
	for c in s:
		if c not in CEscapeSequence:
			buf.append(c)
		else:
			buf.append(CEscapeSequence[c])

	return ''.join(buf)

class FileManager(object):
	def __init__(self, file_list):
		count = len(file_list)
		self.path_list = [''] * count
		self.file_list = [''] * count
		for index in range(count):
			path = os.path.normpath(file_list[index])
			path = path.replace('\\', '/')
			self.path_list[index] = path
			self.file_list[index] = escape_cstr(path)

		self.file_cache = {}

	def __getitem__(self, index):
		return self.file_list[index]

	def get_file_name(self, index):
		return self.file_list[index]

	def get_file_path(self, index):
		return self.path_list[index]

	def get_file_line(self, index, line):
		if index not in self.file_cache:
			path = self.path_list[index]
			lines = open(path).readlines()
			self.file_cache[index] = lines

		return escape_cstr(self.file_cache[index][line - 1].strip())

	def get_loc_line(self, loc):
		return self.get_file_line(loc['file'], loc['line'])


Node_Control = 0
Node_Event = 1

def get_location_name(loc):
	return 'F%dL%dC%d' % (loc['file'], loc['line'], loc['col'])

def get_location_label(loc, file_man):
	return '%s(%d,%d)' % (file_man[loc['file']], loc['line'], loc['col'])

def get_location_node(loc, file_man):
	name = get_location_name(loc)
	label = get_location_label(loc, file_man)
	line = file_man.get_loc_line(loc)
	return {'name': name, 'line': line, 'label': label, 'next': OrderedDict()}

def get_range_node(start, end, file_man):
	start_file = file_man[start['file']]
	if start['file'] == end['file']:
		if start['line'] == end['line']:
			line = file_man.get_loc_line(start)
			if start['col'] == end['col']:
				label = '%s(%d,%d)' % (start_file, start['line'], start['col'])
			else:
				label = '%s(%d,%d~%d)' % (start_file, start['line'], start['col'], end['col'])
		else:
			line = file_man.get_loc_line(start) + '\\n' + file_man.get_loc_line(end)
			label = '%s(%d,%d)~(%d,%d)' % (start_file, start['line'], start['col'], end['line'], end['col'])
	else:
		line = file_man.get_loc_line(start) + '\\n' + file_man.get_loc_line(end)
		end_file = file_man[end['file']]
		label = '%s(%d,%d) ~ %s(%d,%d)' % (start_file, start['line'], start['col'], end_file, end['line'], end['col'])

	name = 'F%dL%dC%d_F%dL%dC%d' % (start['file'], start['line'], start['col'], end['file'], end['line'], end['col'])

	return {'name': name, 'line': line, 'label': label, 'next': OrderedDict()}

def get_control_node(item, file_man):
	edges = item['edges']
	start = edges[0]['start']
	end = edges[-1]['end']
	start = get_range_node(start[0], start[-1], file_man)
	end = get_range_node(end[0], end[-1], file_man)
	start['kind'] = Node_Control
	end['kind'] = Node_Control
	return start, end

def get_event_node(item, file_man):
	loc = item['location']
	if 'ranges' in item:
		ranges = item['ranges']
		start = ranges[0][0]
		end = ranges[-1][-1]
		node = get_range_node(start, end, file_man)
	else:
		node = get_location_node(loc, file_man)

	node['msg'] = [escape_cstr(item['extended_message'])]
	node['kind'] = Node_Event
	return node


def diag2dot(diag, dot_name, file_man):
	node_map = OrderedDict()

	start_name = '@start'
	prev_node = {'name': start_name, 'label': 'start', 'next': OrderedDict(), 'kind': Node_Control}
	node_map[start_name] = prev_node

	path_index = 0
	# path
	for item in diag['path']:
		node_kind = item['kind']
		if node_kind == 'control':
			start, end = get_control_node(item, file_man)
			name = start['name']
			if name not in node_map:
				node_map[name] = start
			else:
				node_map[name]['kind'] |= start['kind']

			if prev_node and name != prev_node['name']:
				prev_next = prev_node['next']
				path_index += prev_node['kind'] != Node_Event
				if name not in prev_next:
					prev_next[name] = [path_index]
				else:
					prev_next[name].append(path_index)

			prev_node = node_map[name]

			name = end['name']
			if name not in node_map:
				node_map[name] = end
			else:
				node_map[name]['kind'] |= end['kind']

			if name != prev_node['name']:
				prev_next = prev_node['next']
				path_index += prev_node['kind'] != Node_Event
				if name not in prev_next:
					prev_next[name] = [path_index]
				else:
					prev_next[name].append(path_index)

			prev_node = node_map[name]

		elif node_kind == 'event':
			loc = get_event_node(item, file_man)
			name = loc['name']
			if not name in node_map:
				node_map[name] = loc
			else:
				prev = node_map[name]
				prev['kind'] |= loc['kind']
				msg = loc['msg'][0]
				if 'msg' not in prev:
					prev['msg'] = loc['msg']
				elif msg not in prev['msg']:
					prev['msg'].append(msg)

			if prev_node and name != prev_node['name']:
				prev_next = prev_node['next']
				if name not in prev_next:
					prev_next[name] = [path_index]
				else:
					prev_next[name].append(path_index)

			prev_node = node_map[name]

	# summary
	end_name = get_location_name(diag['location'])
	diag_category = escape_cstr(diag['category'])
	diag_type = escape_cstr(diag['type'])
	diag_desc = escape_cstr(diag['description'])
	if end_name in node_map:
		end = node_map[end_name]
		if 'msg' in end:
			if diag_desc not in end['msg']:
				end['msg'].append(msg)
		else:
			end['msg'] = [diag_desc]
	else:
		end = get_location_node(diag['location'], file_man)
		end['msg'] = [diag_desc]
		end['kind'] = Node_Event
		node_map[end_name] = end

		if end_name != prev_node['name']:
			prev_next = prev_node['next']
			if end_name not in prev_node['next']:
				prev_next[end_name] = [path_index]
			else:
				prev_next[end_name].append(path_index)

	# reduce arrow index
	index_list = list(range(path_index + 1))
	for node in node_map.values():
		if node['name'] == start_name:
			continue
		if node['kind'] != Node_Event and len(node['next']) == 1:
			for index in node['next'].values()[0]:
				while index > 0 and index <= path_index and index_list[index] > index_list[index - 1]:
					index_list[index] -= 1
					index += 1

	# dot file
	stmt_list = []
	stmt_list.append('digraph "%s" {\n' % escape_cstr(dot_name))
	stmt_list.append('node [shape=plaintext];\n')

	event_nodes = set(node['name'] for node in node_map.values() if node['kind'] == Node_Event)

	for name, node in node_map.items():
		if name == start_name:
			name = 'start'
			stmt_list.append('\t%s [shape=ellipse, color=green, style=filled];\n' % name)
		elif name == end_name:
			stmt_list.append('\t%s [fontcolor=red, label="%s\\n%s\\nCategory: %s\\nType: %s\\n%s"];\n' \
			% (name, node['label'], node['line'], diag_category, diag_type, "\\n".join(node['msg'])))
		elif 'msg' in node and node['msg']:
			stmt_list.append('\t%s [shape=plaintext, fontcolor=blue, label="%s\\n%s\\n%s"];\n' \
			% (name, node['label'], node['line'], "\\n".join(node['msg'])))
		else:
			stmt_list.append('\t%s [shape=plaintext, label="%s\\n%s"];\n' \
			% (name, node['label'], node['line']))

		if node['kind'] == Node_Event:
			for next_name, arrow_index in node['next'].items():
				label = ",".join(str(index) for index in arrow_index)
				#label = ",".join(str(index_list[index]) for index in arrow_index)
				stmt_list.append('\t%s -> %s [color=deepskyblue, fontcolor=deepskyblue, label="%s"];\n' \
				% (name, next_name, label))
		else:
			for next_name, arrow_index in node['next'].items():
				label = ",".join(str(index) for index in arrow_index)
				#label = ",".join(str(index_list[index]) for index in arrow_index)
				if next_name == end_name:
					stmt_list.append('\t%s -> %s [color=crimson, fontcolor=crimson, label="%s"];\n' \
					% (name, next_name, label))
				elif next_name in event_nodes:
					stmt_list.append('\t%s -> %s [color=orange, fontcolor=orange, label="%s"];\n' \
					% (name, next_name, label))
				else:
					stmt_list.append('\t%s -> %s [label="%s"];\n' % (name, next_name, label))

	stmt_list.append('}\n')

	return ''.join(stmt_list)

def diag_plist2dot(path):
	obj = parse_plist_file(path)
	diagnostics = obj['diagnostics']
	if not diagnostics:
		return

	file_man = FileManager(obj['files'])

	base, ext = os.path.splitext(path)
	index = 0
	base = os.path.normpath(base)
	base_name = os.path.basename(base)
	for diag in diagnostics:
		doc = diag2dot(diag, base_name, file_man)
		base_path = base + '-' + str(index)
		dot_path = base_path + '.gv'
		with open(dot_path, 'wb') as ofp:
			ofp.write(doc.encode('utf-8'))

		img_path = base_path + '.pdf'
		subprocess.call(['dot', '-Tpdf', dot_path, '-o', img_path])
		index += 1

def diag_plist2dot_dir(path):
	for root, dirs, file_man in os.walk(path):
		for name in file_man:
			if name.endswith('.plist'):
				full_path = os.path.join(root, name)
				diag_plist2dot(full_path)

def _main():
	for path in sys.argv[1:]:
		if os.path.isfile(path):
			diag_plist2dot(path)
		elif os.path.isdir(path):
			diag_plist2dot_dir(path)
		elif '*' in path or '?' in path:
			for full_path in glob.glob(path):
				if os.path.isfile(full_path):
					diag_plist2dot(full_path)
				elif os.path.isdir(full_path):
					diag_plist2dot_dir(full_path)

if __name__ == '__main__':
	_main()
