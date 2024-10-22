import sys
import os.path

def get_exe_file_list(file_size_map, root, path):
	folder = os.path.join(root, path)
	if not os.path.isdir(folder):
		return
	items = os.listdir(folder)
	for name in items:
		if name.startswith('api-ms'):
			continue
		ext = os.path.splitext(name)[1].lower()
		if ext not in ('.exe', '.dll', '.pyd'):
			continue
		path = os.path.join(folder, name)
		size = os.path.getsize(path)
		if size in file_size_map:
			file_size_map[size].append(path)
		else:
			file_size_map[size] = [path]

def cmp_file_list(items):
	path = items.pop(0)
	with open(path, 'rb') as fd:
		content = fd.read()
	same = [path]
	index = 0
	while index < len(items):
		path = items[index]
		index += 1
		with open(path, 'rb') as fd:
			doc = fd.read()
		if content == doc:
			index -= 1
			items.pop(index)
			same.append(path)
	if len(same) > 1:
		print('same file:', '\n\t'.join(same))

def find_same_file(root):
	file_size_map = {} # file size => [path list]
	get_exe_file_list(file_size_map, root, 'bin')
	get_exe_file_list(file_size_map, root, r'lib\site-packages\lldb')
	for items in file_size_map.values():
		while len(items) > 1:
			cmp_file_list(items)

if __name__ == '__main__':
	if len(sys.argv) > 1 and os.path.isdir(sys.argv[1]):
		find_same_file(sys.argv[1])
	else:
		print(f'Usage: {sys.argv[0]} LLVM folder')
