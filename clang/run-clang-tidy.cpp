// cl /EHsc /std:c++20 /O2 /W4 /MD /DNDEBUG /DNOMINMAX /DWIN32_LEAN_AND_MEAN /DSTRICT_TYPED_ITEMIDS /D_CRT_SECURE_NO_WARNINGS /D_SCL_SECURE_NO_WARNINGS run-clang-tidy.cpp
// clang-cl /EHsc /std:c++20 /O2 /W4 -Wextra -Wshadow -Wimplicit-fallthrough -Wformat=2 -Wundef -Wcomma /MD /DNDEBUG /DNOMINMAX /DWIN32_LEAN_AND_MEAN /DSTRICT_TYPED_ITEMIDS /D_CRT_SECURE_NO_WARNINGS /D_SCL_SECURE_NO_WARNINGS run-clang-tidy.cpp
// g++ -std=gnu++20 -O2 -Wall -Wextra -Wshadow -Wimplicit-fallthrough -Wformat=2 -Wundef -DNDEBUG -DNOMINMAX -DWIN32_LEAN_AND_MEAN -DSTRICT_TYPED_ITEMIDS -D_CRT_SECURE_NO_WARNINGS -D_SCL_SECURE_NO_WARNINGS run-clang-tidy.cpp -lshlwapi

#include <cstdlib>
#include <cstdio>
#include <cstdint>
#include <string>
#include <string_view>
#include <vector>
#include <map>
#include <algorithm>
#include <memory>
#include <atomic>
#include <windows.h>
#include <shlwapi.h>

#ifdef _MSC_VER
#pragma comment(lib, "shlwapi.lib")
#endif

namespace {

constexpr bool IsDigit(int ch) noexcept {
	return ch >= '0' && ch <= '9';
}

struct JsonValue;
using JsonValuePtr = std::unique_ptr<JsonValue>;
using JsonObject = std::map<std::string, JsonValuePtr, std::less<>>;
using JsonArray = std::vector<JsonValuePtr>;

struct JsonValue {
	enum class Type {
		Number,
		String,
		Object,
		Array,
	};

	Type type;
	std::string value;
	std::unique_ptr<JsonObject> object;
	std::unique_ptr<JsonArray> array;

	JsonValue(Type type_, std::string value_): type{type_} {
		value = std::move(value_);
	}
	JsonValue(std::unique_ptr<JsonObject>& object_): type{Type::Object} {
		object.swap(object_);
	}
	JsonValue(std::unique_ptr<JsonArray>& array_): type{Type::Array} {
		array.swap(array_);
	}

	bool GetStringValue(std::string_view key, std::string &value_) const {
		if (type == JsonValue::Type::Object && object) {
			const auto it = object->find(key);
			if (it != object->end() && it->second && it->second->type == JsonValue::Type::String) {
				value_ = it->second->value;
				return true;
			}
		}
		return false;
	}
};

class JsonParser {
	std::string_view doc;
	size_t index = 0;

	static constexpr bool IsWhiteSpace(uint8_t ch) noexcept {
		return ch <= ' ';
	}
	static constexpr bool IsControl(uint8_t ch) noexcept {
		return ch < ' ';
	}
	static constexpr bool IsWordChar(uint8_t ch) noexcept {
		return (ch >= '0' && ch <= '9')
			|| (ch >= 'a' && ch <= 'z')
			|| (ch >= 'A' && ch <= 'Z')
			|| ch == '+' || ch == '-'
			|| ch == '_' || ch == '.'
			|| ch >= 0x80;
	}

	std::string ScanString() {
		std::string value;
		while (index < doc.length()) {
			const char ch = doc[index++];
			if (ch == '\"' || IsControl(ch)) {
				break;
			}
			if (ch == '\\' && index < doc.length()) {
				const char chNext = doc[index++];
				switch (chNext) {
				case '\"':
				case '\\':
				case '/':
					value.push_back(chNext);
					break;
				case 'b':
					value.push_back('\b');
					break;
				case 'f':
					value.push_back('\f');
					break;
				case 'n':
					value.push_back('\n');
					break;
				case 'r':
					value.push_back('\r');
					break;
				case 't':
					value.push_back('\t');
					break;
				//case 'u':
				//	break;
				default:
					value.push_back('\\');
					if (IsControl(chNext)) {
						return value;
					}
					value.push_back(chNext);
					break;
				}
			} else {
				value.push_back(ch);
			}
		}
		return value;
	}

	JsonValuePtr ParseValue() {
		while (index < doc.length()) {
			const uint8_t ch = doc[index++];
			switch (ch) {
			case '[':
				return ParseArray();

			case '{':
				return ParseObject();

			case '\"': {
				const std::string value = ScanString();
				return std::make_unique<JsonValue>(JsonValue::Type::String, value);
			} break;

			default:
				if (IsWordChar(ch)) {
					const size_t start = index - 1;
					while (index < doc.length() && IsWordChar(doc[index])) {
						++index;
					}
					const std::string value(doc.substr(start, index - start));
					return std::make_unique<JsonValue>(JsonValue::Type::Number, value);
				}
				if (!IsWhiteSpace(ch)) {
					fprintf(stderr, "%s unexpected character %02X at %zu\n", __func__, ch, index);
					index = doc.length();
					return {};
				}
				break;
			}
		}
		return {};
	}

	JsonValuePtr ParseArray() {
		std::unique_ptr<JsonArray> array = std::make_unique<JsonArray>();
		while (index < doc.length()) {
			const uint8_t ch = doc[index];
			switch (ch) {
			case ',':
				++index;
				break;

			case ']':
				++index;
				return std::make_unique<JsonValue>(array);

			default:
				if (IsWhiteSpace(ch)) {
					++index;
				} else {
					auto value = ParseValue();
					if (value) {
						array->push_back(std::move(value));
					}
				}
				break;
			}
		}
		return std::make_unique<JsonValue>(array);
	}

	JsonValuePtr ParseObject() {
		std::unique_ptr<JsonObject> object = std::make_unique<JsonObject>();
		std::string key;
		bool hasKey = false;
		while (index < doc.length()) {
			const uint8_t ch = doc[index];
			switch (ch) {
			case ',':
				++index;
				break;

			case ':':
				++index;
				if (hasKey) {
					hasKey = false;
					auto value = ParseValue();
					if (value) {
						object->insert_or_assign(key, std::move(value));
					}
				}
				break;

			case '}':
				++index;
				return std::make_unique<JsonValue>(object);

			default:
				if (IsWhiteSpace(ch)) {
					++index;
				} else if (!hasKey) {
					const auto value = ParseValue();
					if (value && value->type < JsonValue::Type::Object) {
						key = value->value;
						hasKey = true;
					}
				} else {
					fprintf(stderr, "%s unexpected character %02X at %zu\n", __func__, ch, index);
					index = doc.length();
				}
				break;
			}
		}
		return std::make_unique<JsonValue>(object);
	}

public:
	JsonParser(std::string_view doc_) noexcept : doc{doc_} {
		// URF-8 BOM
		if (doc[0] == '\xEF' && doc[1] == '\xBB' && doc[2] == '\xBF') {
			doc.remove_prefix(3);
		}
	}
	JsonValuePtr Parse() {
		return ParseValue();
	}
};

std::vector<std::string> pathList;
std::atomic<uint32_t> pathIndex;
char clangTidyPath[MAX_PATH];
std::string commandLinePrefix;
HANDLE hStdOutput;
HANDLE hStdError;

inline bool PathIsFile(const char *path) noexcept {
	const DWORD attr = GetFileAttributesA(path);
	return (attr & FILE_ATTRIBUTE_DIRECTORY) == 0;
}

bool FindClangTidyPath() noexcept {
	char dir[MAX_PATH]{};
	GetModuleFileNameA(nullptr, dir, sizeof(dir));
	char path[MAX_PATH]{};
	PathCombineA(path, dir, "clang-tidy.exe");
	if (PathIsFile(path)) {
		memcpy(clangTidyPath, path, sizeof(path));
		return true;
	}

	if (SearchPathA(nullptr, "clang-tidy.exe", nullptr, sizeof(path), path, nullptr)) {
		GetFullPathNameA(path, sizeof(clangTidyPath), clangTidyPath, nullptr);
		return true;
	}
	return false;
}

std::string FindCompileDatebase(std::string &directory) {
	char dir[MAX_PATH]{};
	if (!directory.empty()) {
		PathCombineA(dir, directory.c_str(), "compile_commands.json");
		if (PathIsFile(dir)) {
			return dir;
		}
	}

	GetCurrentDirectoryA(sizeof(dir), dir);
	while (true) {
		char path[MAX_PATH]{};
		PathCombineA(path, dir, "compile_commands.json");
		if (PathIsFile(path)) {
			directory = dir;
			return path;
		}
		if (PathIsRootA(dir)) {
			break;
		}
		PathRemoveFileSpecA(dir);
	}
	return "";
}

void ParseCompileDatebase(const char *databasePath) {
	HANDLE hFile = CreateFileA(databasePath,
						GENERIC_READ,
						FILE_SHARE_READ | FILE_SHARE_WRITE,
						nullptr, OPEN_EXISTING,
						FILE_ATTRIBUTE_NORMAL,
						nullptr);
	if (hFile == INVALID_HANDLE_VALUE) {
		return;
	}

	// https://clang.llvm.org/docs/JSONCompilationDatabase.html
	constexpr DWORD minSize = sizeof(R"(["file":""])");
	LARGE_INTEGER fileSize;
	fileSize.QuadPart = 0;
	if (!GetFileSizeEx(hFile, &fileSize) || fileSize.QuadPart < minSize) {
		CloseHandle(hFile);
		return;
	}

	std::string doc;
	doc.resize(fileSize.QuadPart + 1);
	DWORD cbData = 0;
	const BOOL bReadSuccess = ReadFile(hFile, doc.data(), (DWORD)(fileSize.QuadPart), &cbData, nullptr);
	CloseHandle(hFile);
	if (!bReadSuccess || cbData < minSize) {
		return;
	}

	JsonParser parser(doc);
	const auto database = parser.Parse();
	if (database && database->type == JsonValue::Type::Array && database->array) {
		std::string file;
		for (const auto &it : *database->array) {
			if (it && it->GetStringValue("file", file)) {
				if (PathIsRelativeA(file.c_str())) {
					std::string dir;
					if (it->GetStringValue("directory", dir)) {
						char path[MAX_PATH];
						PathCombineA(path, dir.c_str(), file.c_str());
						file = path;
					}
				}
				pathList.push_back(file);
			}
		}
	}
}

VOID CALLBACK WorkCallback([[maybe_unused]] PTP_CALLBACK_INSTANCE instance, [[maybe_unused]] PVOID context, [[maybe_unused]] PTP_WORK work) {
	const uint32_t pathCount = static_cast<uint32_t>(pathList.size());
	while (true) {
		const uint32_t index = pathIndex.fetch_add(1, std::memory_order_relaxed);
		if (index >= pathCount) {
			break;
		}

		PROCESS_INFORMATION procInfo{};
		STARTUPINFOA startInfo{};
		startInfo.cb = sizeof(STARTUPINFO);
		startInfo.hStdInput = INVALID_HANDLE_VALUE;
		startInfo.hStdOutput = hStdOutput;
		startInfo.hStdError = hStdError;
		startInfo.dwFlags = STARTF_USESTDHANDLES;

		const std::string path = pathList[index];
		std::string commandLine = commandLinePrefix + path + "\"";
		if (!CreateProcessA(clangTidyPath, commandLine.data(),
			nullptr, nullptr, TRUE, 0, nullptr, nullptr,
			&startInfo, &procInfo)) {
			fprintf(stderr, "run clang-tidy fail: %s\n", commandLine.c_str());
		} else {
			WaitForSingleObject(procInfo.hProcess, INFINITE);
			CloseHandle(procInfo.hProcess);
			CloseHandle(procInfo.hThread);
		}
	}
}

}

int main(int argc, char *argv[]) {
	uint32_t jobCount = 1;
	std::string directory;
	for (int i = 1; i < argc; i++) {
		const char *arg = argv[i];
		if (arg[0] == '-') {
			bool handled = false;
			switch (arg[1]) {
			case 'j':
				if (IsDigit(arg[2])) {
					handled = true;
					jobCount = atoi(arg + 2);
				}
				break;
			}
			if (!handled) {
				commandLinePrefix += arg;
				commandLinePrefix += ' ';
			}
		}
	}

	if (!FindClangTidyPath()) {
		return 1;
	}

	const std::string path = FindCompileDatebase(directory);
	if (path.empty()) {
		return 2;
	}

	ParseCompileDatebase(path.c_str());
	if (pathList.empty()) {
		return 3;
	}

	hStdOutput = GetStdHandle(STD_OUTPUT_HANDLE);
	hStdError = GetStdHandle(STD_ERROR_HANDLE);
	commandLinePrefix += " -p=\"" + directory + "\" \"";

	SYSTEM_INFO info{};
	GetNativeSystemInfo(&info);
	jobCount = std::min<uint32_t>(jobCount, info.dwNumberOfProcessors - 1);
	jobCount = std::min(jobCount, static_cast<uint32_t>(pathList.size()));
	jobCount = std::max(jobCount, 1U);
	if (jobCount == 1) {
		WorkCallback(nullptr, nullptr, nullptr);
	} else {
		PTP_WORK work = CreateThreadpoolWork(WorkCallback, nullptr, nullptr);
		for (uint32_t i = 0; i < jobCount; i++) {
			SubmitThreadpoolWork(work);
		}
		WaitForThreadpoolWorkCallbacks(work, FALSE);
		CloseThreadpoolWork(work);
	}
	return 0;
}
