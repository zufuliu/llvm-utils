#-*- coding: UTF-8 -*-
"""
http://www.apple.com/DTDs/PropertyList-1.0.dtd
plistObject :
(array | data | date | dict | real | integer | string | true | false )

Collections:
	array:
	dict: key plistObject

Primitive types
	string
	data:	Base-64 encoded
	date:	ISO 8601, YYYY '-' MM '-' DD 'T' HH ':' MM ':' SS 'Z'

Numerical primitives:
	true, false, real, integer

"""
from collections import OrderedDict
import xml.etree.ElementTree as ET
# escape '&', '<', '>'
from xml.sax.saxutils import unescape, escape
import datetime
import base64
import dateutil.parser

def parse_plist(root):
	def parse_true(node):
		return True

	def parse_false(node):
		return False

	def parse_int(node):
		return int(node.text)

	def parse_real(node):
		return float(node.text)

	def parse_string(node):
		return unescape(node.text)

	def parse_date(node):
		value = unescape(node.text)
		return dateutil.parser.parse(value)

	def parse_data(node):
		value = unescape(node.text)
		return base64.b64decode(value)

	node_map = {
		'true': parse_true,
		'false': parse_false,
		'integer': parse_int,
		'real': parse_real,
		'string': parse_string,
		'date': parse_date,
		'data': parse_data,
		'array': None,
		'dict': None,
	}

	def parse_array(node):
		items = []

		for child in node:
			tag = child.tag
			items.append(node_map[tag](child))

		return items

	def parse_dict(node):
		result = OrderedDict()

		key = None
		for child in node:
			tag = child.tag
			if tag == 'key':
				key = unescape(child.text)
			else:
				if key is None:
					raise Exception('missing plist dict key for tag:' + tag)
				value = node_map[tag](child)
				result[key] = value
				key = None

		return result

	node_map['array'] = parse_array
	node_map['dict'] = parse_dict

	result = parse_array(root)
	if len(result) == 1:
		return result[0]
	return result

def parse_plist_file(path):
	tree = ET.parse(path)
	root = tree.getroot()

	if root.tag != 'plist':
		raise Exception('invalid plist root tag:' + root.tag)

	return parse_plist(root)

def write_plist(obj, indent='\t'):
	if isinstance(indent, int):
		indent = ' ' * indent

	def encode_value(value, current_indent_level):
		if value is True:
			yield '<true/>'
		elif value is False:
			yield '<false/>'
		elif isinstance(value, (int, long)):
			yield '<integer>' + str(value) + '</integer>'
		elif isinstance(value, float):
			yield '<real>' + str(value) + '</real>'
		elif isinstance(value, basestring):
			yield '<string>' + escape(value) + '</string>'
		elif isinstance(value, datetime.datetime):
			yield '<date>' + value.strftime('%Y-%m-%dT%H:%M:%SZ') +  '</date>'
		elif isinstance(value, (bytes, bytearray)):
			yield '<data>' + escape(base64.b64encode(value)) + '</data>'
		else:
			if isinstance(value, (list, tuple, set)):
				chunks = encode_array(value, current_indent_level)
			elif isinstance(value, dict):
				chunks = encode_dict(value, current_indent_level)
			elif hasattr(value, '__iter__'):
				chunks = encode_array(value, current_indent_level)
			elif hasattr(value, '__dict__'):
				chunks = encode_dict(value.__dict__, current_indent_level)
			else:
				raise ValueError('unsupported plist type:' + type(value))
			for chunk in chunks:
				yield chunk

	def encode_array(array_obj, current_indent_level):
		yield '<array>'
		current_indent_level += 1
		newline_indent = '\n' + indent * current_indent_level

		for value in array_obj:
			yield newline_indent
			chunks = encode_value(value, current_indent_level)
			for chunk in chunks:
				yield chunk

		current_indent_level -= 1
		yield '\n' + indent * current_indent_level
		yield '</array>'

	def encode_dict(dict_obj, current_indent_level):
		yield '<dict>'
		current_indent_level += 1
		newline_indent = '\n' + indent * current_indent_level

		for key, value in dict_obj.items():
			yield newline_indent
			yield '<key>' + escape(str(key)) + '</key>'
			yield newline_indent
			chunks = encode_value(value, current_indent_level)
			for chunk in chunks:
				yield chunk

		current_indent_level -= 1
		yield '\n' + indent * current_indent_level
		yield '</dict>'

	def dump_plist(obj):
		yield """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
"""
		chunks = encode_value(obj, 0)
		for chunk in chunks:
			yield chunk
		yield '\n</plist>\n'

	chunks = dump_plist(obj)
	return ''.join(chunks)

def write_plist_file(obj, path):
	doc = write_plist(obj)
	with open(path, 'wb') as ofp:
		ofp.write(doc.encode('utf-8'))
