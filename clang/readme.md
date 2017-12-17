# Clang Static Analyze Utils

## Usage
1. install GraphViz from http://graphviz.org/, add bin folder to PATH.

2. Run clang static analyze using following options:

	clang --analyze -Xanalyzer -analyzer-output=plist-multi-file

3. Run cdiag2dot to convert output plist file to PDF.

	cdiag2dot.py xxx.plist
