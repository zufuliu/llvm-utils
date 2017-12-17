#!/usr/bin/env python
#-*- coding: UTF-8 -*-
import sys
import os.path
import glob
import json
from collections import OrderedDict
from plist import write_plist

def json_loads(path):
	return json.JSONDecoder(object_pairs_hook=OrderedDict).decode(open(path).read())

def json2plist(path):
	obj = json_loads(path)
	base, ext = os.path.splitext(path)
	out_path = base + '.plist'
	with open(out_path, 'wb') as ofp:
		ofp.write(write_plist(obj).encode('utf-8'))

def json2plist_dir(path):
	for root, dirs, files in os.walk(path):
		for name in files:
			if name.endswith('.json'):
				full_path = os.path.join(root, name)
				json2plist(full_path)

def _main():
	for path in sys.argv[1:]:
		if os.path.isfile(path):
			json2plist(path)
		elif os.path.isdir(path):
			json2plist_dir(path)
		elif '*' in path or '?' in path:
			for full_path in glob.glob(path):
				if os.path.isfile(full_path):
					json2plist(full_path)
				elif os.path.isdir(full_path):
					json2plist_dir(full_path)

if __name__ == '__main__':
	_main()
