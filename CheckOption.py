#!/usr/bin/env python3
import sys
import os.path
import subprocess
import string
import xml.dom.minidom

def decode_stdout(doc):
	if not doc:
		return ''
	try:
		return doc.decode('utf-8')
	except UnicodeDecodeError:
		try:
			return doc.decode(sys.stdout.encoding)
		except UnicodeDecodeError:
			return doc.decode(sys.getdefaultencoding())

def get_clang_cl_help():
	with subprocess.Popen(['clang-cl.exe', '/?'], stdout=subprocess.PIPE) as proc:
		doc = proc.stdout.read()
		return decode_stdout(doc)

def get_visual_studio_cl_rule_path():
	result = []
	path = os.getenv('ProgramFiles(x86)')
	if not path:
		path = r'C:\Program Files (x86)'
	vswhere = os.path.join(path, r'Microsoft Visual Studio\Installer\vswhere.exe')
	# Visual Studio 2019
	with subprocess.Popen([vswhere, '-property', 'installationPath', '-prerelease', '-version', '[16.0,17.0]'], stdout=subprocess.PIPE) as proc:
		doc = proc.stdout.read()
		lines = decode_stdout(doc).splitlines()
		for line in lines:
			if os.path.exists(line):
				path = os.path.join(line, r'MSBuild\Microsoft\VC\v160\1033\cl.xml')
				if os.path.isfile(path):
					print('find:', path)
					result.append(path)
				path = os.path.join(line, r'MSBuild\Microsoft\VC\v150\1033\cl.xml')
				if os.path.isfile(path):
					print('find:', path)
					result.append(path)
	# Visual Studio 2017
	with subprocess.Popen([vswhere, '-property', 'installationPath', '-prerelease', '-version', '[15.0,16.0]'], stdout=subprocess.PIPE) as proc:
		doc = proc.stdout.read()
		lines = decode_stdout(doc).splitlines()
		for line in lines:
			if os.path.exists(line):
				path = os.path.join(line, r'Common7\IDE\VC\VCTargets\1033\cl.xml')
				if os.path.isfile(path):
					print('find:', path)
					result.append(path)
	return result

def parse_clang_cl_help(doc):
	# cl.exe compatibility options
	supported = set()
	for line in doc.splitlines():
		line = line.strip()
		if line.startswith('/'):
			item = line.split()[0]
			if len(item) >= 1 and item[1] in string.ascii_letters:
				index = item.find('<')
				if index > 0:
					item = item[:index]
				if item[-1] == ':':
					item = item[:-1]
				supported.add(item)
	return supported

def parse_clang_cl_ignored_options(path):
	print('parse:', path)
	ignored = set()
	with xml.dom.minidom.parse(path) as dom:
		doc = dom.documentElement
		assert doc.tagName == 'Project'
		for node in doc.getElementsByTagName('Target'):
			if node.getAttribute('Name') == 'BeforeClCompile':
				for child in node.getElementsByTagName('ItemGroup'):
					for tag in child.getElementsByTagName('ClCompile'):
						for item in tag.getElementsByTagName('*'):
							if not item.childNodes:
								ignored.add(item.tagName)
	return ignored

def parse_cl_rule_xml(path, options, switchMap):
	def fix_swicth(value):
		value = value.strip()
		if not value:
			return ''
		return '/' + value

	print('parse:', path)
	with xml.dom.minidom.parse(path) as dom:
		doc = dom.documentElement
		assert doc.tagName == 'Rule'
		for node in doc.getElementsByTagName('*'):
			tagName = node.tagName
			if not tagName.endswith('Property'):
				continue
			name = node.getAttribute('Name')
			if name in options:
				continue
			switch = fix_swicth(node.getAttribute('Switch'))
			reverseSwitch = fix_swicth(node.getAttribute('ReverseSwitch'))
			values = {}
			if tagName == 'EnumProperty':
				for enumValue in node.getElementsByTagName('EnumValue'):
					valueSwitch = fix_swicth(enumValue.getAttribute('Switch'))
					if valueSwitch:
						switchMap[valueSwitch] = name
					valueName = enumValue.getAttribute('Name')
					values[valueName] = {
						'Name': valueName,
						'Switch': valueSwitch,
						'DisplayName': enumValue.getAttribute('DisplayName'),
						'Description': enumValue.getAttribute('Description'),
					}
			if switch or reverseSwitch or values or tagName == 'DynamicEnumProperty':
				if switch:
					switchMap[switch] = name
				if reverseSwitch:
					switchMap[reverseSwitch] = name
				options[name] = {
					'Name': name,
					'Type': tagName,
					'DisplayName': node.getAttribute('DisplayName'),
					'Switch': switch,
					'ReverseSwitch': reverseSwitch,
					'Description': node.getAttribute('Description'),
					'Options': values,
				}
			else:
				switch = node.getAttribute('IncludeInCommandLine')
				if switch != 'false':
					print('    ignore:', tagName, name)
	return options

def dump_cl_rule_as_yaml(path, options):
	with open(path, 'w', encoding='utf-8') as fd:
		fd.write('Rule:\n')
		for option in options.values():
			fd.write(f"  - {option['Type']}: {option['Name']}\n")
			fd.write(f"    DisplayName: {option['DisplayName']}\n")
			fd.write(f"    Description: {option['Description']}\n")
			value = option['Switch']
			if value:
				fd.write(f"    Switch: {value}\n")
			value = option['ReverseSwitch']
			if value:
				fd.write(f"    ReverseSwitch: {value}\n")
			values = option['Options']
			if values:
				fd.write("    Options:\n")
				for value in values.values():
					fd.write(f"      - Name: {value['Name']}\n")
					fd.write(f"        Switch: {value['Switch'] or 'None'}\n")
					fd.write(f"        DisplayName: {value['DisplayName']}\n")
					fd.write(f"        Description: {value['Description']}\n")

def main():
	doc = get_clang_cl_help()
	supported = parse_clang_cl_help(doc)
	path = r'VS2017\LLVM\LLVM.Common.targets'
	ignored = parse_clang_cl_ignored_options(path)

	options = {}
	switchMap = {}
	result = get_visual_studio_cl_rule_path()
	for path in result:
		parse_cl_rule_xml(path, options, switchMap)
	dump_cl_rule_as_yaml('cl.yml', options)

	# remove previous ignored but now supported options
	for item in supported:
		if item in switchMap:
			name = switchMap[item]
			if name in ignored:
				print('supported option:', name, item)

	hardcoded = set([
		# error
		'CompileAsManaged',
		'CompileAsWinRT',
		'EnableModules',
		# unsupported
		'BasicRuntimeChecks',
		'LanguageStandard_C',
		# full or partial supported
		'AssemblerOutput',
		'CompileAs',
		'ControlFlowGuard',
		'DebugInformationFormat',
		'EnableEnhancedInstructionSet',
		'ExceptionHandling',
		'StructMemberAlignment',
		'LanguageStandard',
	])
	ignored |= hardcoded
	# find unsupported options
	unsupported = {}

	def check_switch(name, option, value):
		if not value:
			return
		if value not in supported:
			if name not in ignored:
				unsupported[name] = option
			if name not in hardcoded and ':' in value:
				value = value[:value.index(':')]
				if value in supported:
					print('maybe supported option:', name, value)
		elif name in ignored:
			print('supported option:', name, value)

	for option in options.values():
		name = option['Name']
		value = option['Switch']
		check_switch(name, option, value)
		value = option['ReverseSwitch']
		check_switch(name, option, value)
		values = option['Options']
		if values:
			for item in values.values():
				value = item['Switch']
				check_switch(name, option, value)

	print('total option count:', len( options), 'unsupported:', len(unsupported))
	if unsupported:
		unsupported = dict(sorted(unsupported.items()))
		dump_cl_rule_as_yaml('new-unsupported.yml', unsupported)
	for name in ignored - hardcoded:
		if name in options:
			unsupported[name] = options[name]
	unsupported = dict(sorted(unsupported.items()))
	dump_cl_rule_as_yaml('all-unsupported.yml', unsupported)

if __name__ == '__main__':
	main()
