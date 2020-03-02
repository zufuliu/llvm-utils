# Clang Utils

## clang-cl for Python 3 distutils
See `clang-cl-py3.diff` for the changes on hwo to use clang-cl as distutils compiler.
After apply these changes, you can build your extension with

	python setup.py build --compiler=clang-cl 

## Clang Static Analyze Utils

*These scripts are deprecated in favor of HTML output by using:*

	clang --analyze -Xanalyzer -analyzer-output=html
	clang-cl --analyze -Xclang -analyzer-output=html

### Usage
1. Install GraphViz from http://graphviz.org/, add bin folder to PATH.

2. Run clang static analyze using following options:

	clang --analyze -Xanalyzer -analyzer-output=plist-multi-file
	clang-cl --analyze -Xclang -analyzer-output=plist-multi-file

3. Run cdiag2dot to convert output plist file to PDF.

	cdiag2dot.py xxx.plist
