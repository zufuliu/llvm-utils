#!/usr/bin/env python3
import sys
import os.path
import subprocess
import string
import xml.dom.minidom
import ctypes

CP_ACP = 'cp' + str(ctypes.windll.kernel32.GetACP())

def decode_stdout(doc):
	if not doc:
		return ''
	try:
		return doc.decode('utf-8')
	except UnicodeDecodeError:
		return doc.decode(CP_ACP)

def get_clang_cl_help(filename, saveLog=True):
	with subprocess.Popen([filename, '/?'], stdout=subprocess.PIPE) as proc:
		doc = proc.stdout.read()
		if saveLog:
			path = os.path.splitext(os.path.basename(filename))[0] + '.log'
			with open(path, 'wb') as fd:
				fd.write(doc)
		return decode_stdout(doc)

def get_msvc_rule_path(filename):
	result = []
	path = os.getenv('ProgramFiles(x86)') or r'C:\Program Files (x86)'
	vswhere = os.path.join(path, r'Microsoft Visual Studio\Installer\vswhere.exe')
	# Visual Studio 2022
	with subprocess.Popen([vswhere, '-property', 'installationPath', '-prerelease', '-version', '[17.0,18.0)'], stdout=subprocess.PIPE) as proc:
		doc = proc.stdout.read()
		lines = decode_stdout(doc).splitlines()
		for line in lines:
			if os.path.exists(line):
				path = os.path.join(line, r'MSBuild\Microsoft\VC\v170\1033', filename)
				if os.path.isfile(path):
					print('find:', path)
					result.append(path)
				path = os.path.join(line, r'MSBuild\Microsoft\VC\v160\1033', filename)
				if os.path.isfile(path):
					print('find:', path)
					result.append(path)
				path = os.path.join(line, r'MSBuild\Microsoft\VC\v150\1033', filename)
				if os.path.isfile(path):
					print('find:', path)
					result.append(path)
	# Visual Studio 2019
	with subprocess.Popen([vswhere, '-property', 'installationPath', '-prerelease', '-version', '[16.0,17.0)'], stdout=subprocess.PIPE) as proc:
		doc = proc.stdout.read()
		lines = decode_stdout(doc).splitlines()
		for line in lines:
			if os.path.exists(line):
				path = os.path.join(line, r'MSBuild\Microsoft\VC\v160\1033', filename)
				if os.path.isfile(path):
					print('find:', path)
					result.append(path)
				path = os.path.join(line, r'MSBuild\Microsoft\VC\v150\1033', filename)
				if os.path.isfile(path):
					print('find:', path)
					result.append(path)
	# Visual Studio 2017
	with subprocess.Popen([vswhere, '-property', 'installationPath', '-prerelease', '-version', '[15.0,16.0)'], stdout=subprocess.PIPE) as proc:
		doc = proc.stdout.read()
		lines = decode_stdout(doc).splitlines()
		for line in lines:
			if os.path.exists(line):
				path = os.path.join(line, r'Common7\IDE\VC\VCTargets\1033', filename)
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
					if ':' in item:
						item = item + '*'
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

def parse_msvc_rule_xml(path, options, switchMap):
	def fix_swicth(value):
		value = value.strip()
		return '/' + value if value else ''

	print('parse:', path)
	with xml.dom.minidom.parse(path) as dom:
		doc = dom.documentElement
		assert doc.tagName == 'Rule'
		for node in doc.getElementsByTagName('*'):
			tagName = node.tagName
			if not tagName.endswith('Property'):
				continue
			name = node.getAttribute('Name')
			values = {}
			if tagName == 'EnumProperty':
				if name in options:
					values = options[name]['Options']
				for enumValue in node.getElementsByTagName('EnumValue'):
					valueName = enumValue.getAttribute('Name')
					if valueName not in values:
						valueSwitch = fix_swicth(enumValue.getAttribute('Switch'))
						if valueSwitch:
							switchMap[valueSwitch] = name
						values[valueName] = {
							'Name': valueName,
							'Switch': valueSwitch,
							'DisplayName': enumValue.getAttribute('DisplayName'),
							'Description': enumValue.getAttribute('Description'),
						}
			elif name in options:
				continue
			switch = fix_swicth(node.getAttribute('Switch'))
			reverseSwitch = fix_swicth(node.getAttribute('ReverseSwitch'))
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

def dump_msvc_rule_as_yaml(path, options):
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

def check_program_options(llvmName, msvcName, ignored=[], hardcoded=[]):
	doc = get_clang_cl_help(llvmName)
	supported = parse_clang_cl_help(doc)
	prefixList = [item[:-1] for item in supported if item[-1] == '*']

	options = {}
	switchMap = {}
	result = get_msvc_rule_path(f'{msvcName}.xml')
	for path in result:
		parse_msvc_rule_xml(path, options, switchMap)
	dump_msvc_rule_as_yaml(f'{msvcName}.yml', options)

	# remove previous ignored but now supported options
	if ignored:
		for item in supported:
			if item in switchMap:
				name = switchMap[item]
				if name in ignored:
					print(f'supported {msvcName} option:', name, item)

	# find unsupported options
	unsupported = {}

	def check_switch_match_case(name, option, value):
		if not value:
			return
		if value in supported:
			if name in ignored:
				print(f'supported {msvcName} option:', name, value)
			return
		if name not in ignored and name not in hardcoded:
			unsupported[name] = option
		if name not in hardcoded and ':' in value:
			if any(value.startswith(prefix) for prefix in prefixList):
				print(f'maybe supported {msvcName} option:', name, value)

	def check_switch_ignore_case(name, option, value):
		if not value:
			return
		lower = value.lower()
		upper = value.upper()
		if value in supported or lower in supported or upper in supported:
			if name in ignored:
				print(f'supported {msvcName} option:', name, value)
			return
		if name not in ignored and name not in hardcoded:
			unsupported[name] = option
		if name not in hardcoded and ':' in value:
			if any(value.startswith(prefix) or lower.startswith(prefix) or upper.startswith(prefix) for prefix in prefixList):
				print(f'maybe supported {msvcName} option:', name, value)

	check_switch = check_switch_match_case if msvcName == 'cl' else check_switch_ignore_case
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

	print(f'total {msvcName} option count:', len( options), 'unsupported:', len(unsupported))
	if unsupported:
		unsupported = dict(sorted(unsupported.items()))
		dump_msvc_rule_as_yaml(f'{msvcName}-unsupported.yml', unsupported)
	if ignored:
		for name in ignored:
			if name in options:
				unsupported[name] = options[name]
		unsupported = dict(sorted(unsupported.items()))
		dump_msvc_rule_as_yaml(f'all-{msvcName}-unsupported.yml', unsupported)


def check_clang_cl_options():
	path = r'VS2017\LLVM\LLVM.Common.targets'
	ignored = parse_clang_cl_ignored_options(path)
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
	check_program_options('clang-cl.exe', 'cl', ignored=ignored, hardcoded=hardcoded)

def check_lld_link_options():
	hardcoded = set([
		# supported
		'AdditionalLibraryDirectories',
		'AdditionalManifestDependencies',
		'CreateHotPatchableImage',
		'DelayLoadDLLs',
		'EnableCOMDATFolding',
		'EnableUAC',
		'ForceSymbolReferences',
		'GenerateDebugInformation',
		'GenerateManifest',
		'IgnoreSpecificDefaultLibraries',
		'LinkControlFlowGuard',
		'ManifestEmbed',
		'ManifestInput',
		'Natvis',
		'OptimizeReferences',
		'SpecifySectionAttributes',
		'SubSystem',
		'TargetMachine',
	])
	check_program_options('lld-link.exe', 'link', hardcoded=hardcoded)

def check_llvm_lib_options():
	hardcoded = set([
		# supported
		'AdditionalLibraryDirectories',
		'TargetMachine',
	])
	check_program_options('llvm-lib.exe', 'lib', hardcoded=hardcoded)

def check_llvm_rc_options():
	check_program_options('llvm-rc.exe', 'rc')

if __name__ == '__main__':
	check_clang_cl_options()
	check_lld_link_options()
	check_llvm_lib_options()
	check_llvm_rc_options()

