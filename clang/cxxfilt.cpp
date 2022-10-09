// compile inside llvm/lib/Demangle/ folder.
// cl /std:c++20 /EHsc /O2 /GR- /GS- /MD /DNDEBUG /I../../include *.cpp
// clang-cl /std:c++20 /EHsc /O2 /GR- /GS- /MD /DNDEBUG /I../../include *.cpp

#include "llvm/Demangle/Demangle.h"
#include <cstdio>
#include <iostream>

static std::string demangle(const std::string &name) {
	std::string result = llvm::demangle(name);
	constexpr std::string_view prefix = "__imp_";
	if (result == name && name.starts_with(prefix)) {
		const std::string mangled = name.substr(prefix.length());
		std::string undecorated = llvm::demangle(mangled);
		if (undecorated != mangled) {
			result = "import thunk for " + undecorated;
		}
	}
	return result;
}

int main(int argc, char *argv[]) {
	if (argc > 1) {
		for (int index = 1; index < argc; index++) {
			const std::string name = argv[index];
			const std::string result = demangle(name);
			printf("%s\n    %s\n", name.c_str(), result.c_str());
		}
	} else {
		printf(">>> ");
		std::string name;
		while (std::getline(std::cin, name, '\n')) {
			const std::string result = demangle(name);
			printf("%s\n>>> ", result.c_str());
		}
	}
	return 0;
}
