// compile inside llvm/lib/Demangle/ folder.
// cl /std:c++20 /EHsc /O2 /GR- /GS- /MD /DNDEBUG /I../../include *.cpp
// clang-cl /std:c++20 /EHsc /O2 /GR- /GS- /MD /DNDEBUG /I../../include *.cpp

#include "llvm/Demangle/Demangle.h"
#include <cstdio>
#include <iostream>

int main(int argc, char *argv[]) {
	if (argc > 1) {
		for (int index = 1; index < argc; index++) {
			const std::string name = argv[index];
			const std::string result = llvm::demangle(name);
			printf("%s\n    %s\n", name.c_str(), result.c_str());
		}
	} else {
		std::string name;
		while (true) {
			printf(">> ");
			std::getline(std::cin, name, '\n');
			const std::string result = llvm::demangle(name);
			printf("%s\n", result.c_str());
		}
	}
	return 0;
}
