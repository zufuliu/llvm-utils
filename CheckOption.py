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
	# Visual Studio 2019, 2022
	with subprocess.Popen([vswhere, '-sort', '-property', 'installationPath', '-prerelease', '-version', '[16.0,18.0)'], stdout=subprocess.PIPE) as proc:
		doc = proc.stdout.read()
		lines = decode_stdout(doc).splitlines()
		for line in lines:
			if not os.path.exists(line):
				continue
			for version in ['v170', 'v160', 'v150']:
				path = os.path.join(line, rf'MSBuild\Microsoft\VC\{version}\1033', filename)
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
	groups = {'ClCompile': 'cl', 'Link': 'link', 'Lib': 'lib', 'ResourceCompile': 'rc'}
	ignored = {}
	for group in groups.values():
		ignored[group] = set(['SuppressStartupBanner']) # nologo
	with xml.dom.minidom.parse(path) as dom:
		doc = dom.documentElement
		assert doc.tagName == 'Project'
		for node in doc.getElementsByTagName('Target'):
			if node.getAttribute('Name') == 'BeforeClCompile':
				for child in node.getElementsByTagName('ItemGroup'):
					for tag in child.getElementsByTagName('ClCompile'):
						for item in tag.getElementsByTagName('*'):
							if not item.childNodes:
								ignored['cl'].add(item.tagName)
		for node in doc.getElementsByTagName('ItemDefinitionGroup'):
			for child in node.getElementsByTagName('*'):
				if group := groups.get(child.tagName, None):
					for item in child.getElementsByTagName('*'):
						if not item.childNodes and not item.attributes:
							ignored[group].add(item.tagName)
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
				if not switch:
					print('    ignore:', tagName, name)
				else:
					options[name] = {
						'Name': name,
						'Type': tagName,
						'DisplayName': node.getAttribute('DisplayName'),
						'IncludeInCommandLine': switch,
						'Description': node.getAttribute('Description'),
					}
	return options

def dump_msvc_rule_as_yaml(path, options):
	with open(path, 'w', encoding='utf-8') as fd:
		fd.write('Rule:\n')
		for option in options.values():
			fd.write(f"  - {option['Type']}: {option['Name']}\n")
			fd.write(f"    DisplayName: {option['DisplayName']}\n")
			fd.write(f"    Description: {option['Description']}\n")
			if value := option.get('Switch', None):
				fd.write(f"    Switch: {value}\n")
			if value := option.get('ReverseSwitch', None):
				fd.write(f"    ReverseSwitch: {value}\n")
			if value := option.get('IncludeInCommandLine', None):
				fd.write(f"    IncludeInCommandLine: {value}\n")
			if values := option.get('Options', None):
				fd.write("    Options:\n")
				for value in values.values():
					fd.write(f"      - Name: {value['Name']}\n")
					fd.write(f"        Switch: {value['Switch'] or 'None'}\n")
					fd.write(f"        DisplayName: {value['DisplayName']}\n")
					fd.write(f"        Description: {value['Description']}\n")

def check_program_options(llvmName, msvcName, ignored=[], hardcoded=[]):
	doc = get_clang_cl_help(llvmName)
	supported = parse_clang_cl_help(doc)
	if msvcName != 'cl':
		supported = set(value.lower() for value in supported)
	prefixList = [item[:-1] for item in supported if item[-1] == '*']

	options = {}
	switchMap = {}
	result = get_msvc_rule_path(f'{msvcName}.xml')
	for path in result:
		parse_msvc_rule_xml(path, options, switchMap)
	options = dict(sorted(options.items()))
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
		if lower in supported:
			if name in ignored:
				print(f'supported {msvcName} option:', name, value)
			return
		if name not in ignored and name not in hardcoded:
			unsupported[name] = option
		if name not in hardcoded and ':' in value:
			if any(lower.startswith(prefix) for prefix in prefixList):
				print(f'maybe supported {msvcName} option:', name, value)

	check_switch = check_switch_match_case if msvcName == 'cl' else check_switch_ignore_case
	for option in options.values():
		name = option['Name']
		if value := option.get('Switch', None):
			check_switch(name, option, value)
		if value := option.get('ReverseSwitch', None):
			check_switch(name, option, value)
		if values := option.get('Options', None):
			for item in values.values():
				value = item['Switch']
				check_switch(name, option, value)
		if 'IncludeInCommandLine' in option:
			if name not in ignored and name not in hardcoded:
				unsupported[name] = option

	print(f'total {msvcName} option count:', len( options), 'unsupported:', len(unsupported))
	path = f'{msvcName}-unsupported.yml'
	if unsupported:
		unsupported = dict(sorted(unsupported.items()))
		dump_msvc_rule_as_yaml(path, unsupported)
	elif os.path.isfile(path):
		try:
			os.remove(path)
		except Exception:
			pass
	if ignored:
		for name in ignored:
			if name in options:
				unsupported[name] = options[name]
		unsupported = dict(sorted(unsupported.items()))
		dump_msvc_rule_as_yaml(f'all-{msvcName}-unsupported.yml', unsupported)


def check_clang_cl_options(ignored):
	# https://github.com/llvm/llvm-project/tree/main/clang/include/clang/Driver/Options.td
	ignored |= set([
		# error
		'CompileAsManaged',
		'CompileAsWinRT',
		'EnableModules',
		# unsupported
		'BasicRuntimeChecks',
		'SpectreMitigation',
		# handled by MSBuild
		'BuildStlModules',
		'MultiProcessorCompilation',
		'ScanSourceForModuleDependencies',
		'TrackerLogDirectory',
	])
	hardcoded = set([
		# full or partial supported
		'AssemblerOutput',
		'CompileAs',
		'ControlFlowGuard',
		'DebugInformationFormat',
		'EnableEnhancedInstructionSet',
		'ExceptionHandling',
		'ExternalDirectoriesEnv',
		'FloatingPointExceptions',
		'FloatingPointModel',
		'GuardEHContMetadata',
		'LanguageStandard',
		'LanguageStandard_C',
		'StructMemberAlignment',
	])
	check_program_options('clang-cl.exe', 'cl', ignored=ignored, hardcoded=hardcoded)

def check_lld_link_options(ignored):
	# https://github.com/llvm/llvm-project/tree/main/lld/COFF/Options.td
	ignored |= set([
		'LinkTimeCodeGeneration',
		# handled by MSBuild
		'IgnoreImportLibrary',
		'LinkLibraryDependencies',
		'PerUserRedirection',
		'RegisterOutput',
		'TrackerLogDirectory',
		'UseLibraryDependencyInputs',
	])
	hardcoded = set([
		# supported
		'AdditionalLibraryDirectories',
		'AdditionalManifestDependencies',
		'BaseAddress',
		'CreateHotPatchableImage',
		'DelayLoadDLLs',
		'EnableCOMDATFolding',
		'EnableUAC',
		'EntryPointSymbol',
		'ForceSymbolReferences',
		'FunctionOrder',
		'GenerateDebugInformation',
		'GenerateManifest',
		'GenerateMapFile',
		'HeapReserveSize',
		'IgnoreSpecificDefaultLibraries',
		'ImportLibrary',
		'LinkControlFlowGuard',
		'LinkGuardEHContMetadata',
		'LinkGuardSignedReturns',
		'ManifestEmbed',
		'ManifestFile',
		'ManifestInput',
		'MapExports',
		'MergeSections',
		'ModuleDefinitionFile',
		'MSDOSStubFileName',
		'Natvis',
		'OptimizeReferences',
		'OutputFile',
		'Profile',
		'ProgramDatabaseFile',
		'SectionAlignment',
		'ShowProgress',
		'SpecifySectionAttributes',
		'StackReserveSize',
		'StripPrivateSymbols',
		'SubSystem',
		'TargetMachine',
		'Version',
	])
	check_program_options('lld-link.exe', 'link', ignored=ignored, hardcoded=hardcoded)

def check_llvm_lib_options(ignored):
	# https://github.com/llvm/llvm-project/tree/main/llvm/lib/ToolDrivers/llvm-lib/Options.td
	ignored |= set([
		'LinkTimeCodeGeneration',
		# handled by MSBuild
		'LinkLibraryDependencies',
		'TrackerLogDirectory',
		'UseUnicodeResponseFiles',
	])
	hardcoded = set([
		# supported
		'AdditionalLibraryDirectories',
		'TargetMachine',
		'OutputFile',
	])
	check_program_options('llvm-lib.exe', 'lib', ignored=ignored, hardcoded=hardcoded)

def check_llvm_rc_options(ignored):
	# https://github.com/llvm/llvm-project/blob/main/llvm/tools/llvm-rc/Opts.td
	ignored |= set([
		# handled by MSBuild
		'DesigntimePreprocessorDefinitions',
		'TrackerLogDirectory',
	])
	check_program_options('llvm-rc.exe', 'rc', ignored=ignored)

def main():
	ignored = parse_clang_cl_ignored_options(r'VS2017\LLVM\LLVM.Common.targets')
	check_clang_cl_options(ignored['cl'])
	check_lld_link_options(ignored['link'])
	check_llvm_lib_options(ignored['lib'])
	check_llvm_rc_options(ignored['rc'])

if __name__ == '__main__':
	main()
