#!/usr/bin/env python
#-*- coding: UTF-8 -*-
import sys
import os.path
import glob
import json
from plist import parse_plist_file

def json_dumps(obj):
	return json.dumps(obj, indent='\t', separators=(', ', ': '))

def plist2json(path):
	obj = parse_plist_file(path)
	base, ext = os.path.splitext(path)
	out_path = base + '.json'
	with open(out_path, 'wb') as ofp:
		ofp.write(json_dumps(obj).encode('utf-8'))

def plist2json_dir(path):
	for root, dirs, files in os.walk(path):
		for name in files:
			if name.endswith('.plist'):
				full_path = os.path.join(root, name)
				plist2json(full_path)

def _main():
	for path in sys.argv[1:]:
		if os.path.isfile(path):
			plist2json(path)
		elif os.path.isdir(path):
			plist2json_dir(path)
		elif '*' in path or '?' in path:
			for full_path in glob.glob(path):
				if os.path.isfile(full_path):
					plist2json(full_path)
				elif os.path.isdir(full_path):
					plist2json_dir(full_path)

if __name__ == '__main__':
	_main()
