// cl /std:c++20 /EHsc /O2 /GR- /W4 /MD /DNDEBUG /DNOMINMAX /DWIN32_LEAN_AND_MEAN /DSTRICT_TYPED_ITEMIDS /DUNICODE /D_UNICODE /D_CRT_SECURE_NO_WARNINGS /D_SCL_SECURE_NO_WARNINGS run-clang-tidy.cpp
// clang-cl /std:c++20 /EHsc /O2 /GR- /W4 -Wextra -Wshadow -Wimplicit-fallthrough -Wformat=2 -Wundef -Wcomma /MD /DUNICODE /D_UNICODE /DNDEBUG /DNOMINMAX /DWIN32_LEAN_AND_MEAN /DSTRICT_TYPED_ITEMIDS /D_CRT_SECURE_NO_WARNINGS /D_SCL_SECURE_NO_WARNINGS run-clang-tidy.cpp
// g++ -std=gnu++20 -O2 -municode -fno-rtti -Wall -Wextra -Wshadow -Wimplicit-fallthrough -Wformat=2 -Wundef -DNDEBUG -DNOMINMAX -DWIN32_LEAN_AND_MEAN -DUNICODE -D_UNICODE -DSTRICT_TYPED_ITEMIDS -D_CRT_SECURE_NO_WARNINGS -D_SCL_SECURE_NO_WARNINGS run-clang-tidy.cpp -lshlwapi

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
#pragma comment(lib, "user32.lib")
#pragma comment(lib, "shlwapi.lib")
#endif

namespace {

HANDLE hStdOutput;
HANDLE hStdError;

constexpr bool IsDigit(int ch) noexcept {
	return ch >= '0' && ch <= '9';
}

constexpr int GetHexDigit(int ch) noexcept {
	uint32_t diff = ch - '0';
	if (diff < 10) {
		return diff;
	}
	diff = (ch | 0x20) - 'a';
	if (diff < 6) {
		return diff + 10;
	}
	return -1;
}

struct JsonValue;
using JsonValuePtr = std::unique_ptr<JsonValue>;
using JsonObject = std::map<std::wstring, JsonValuePtr, std::less<>>;
using JsonArray = std::vector<JsonValuePtr>;

struct JsonValue {
	enum class Type {
		Number,
		String,
		Object,
		Array,
	};

	Type type;
	std::wstring value;
	std::unique_ptr<JsonObject> object;
	std::unique_ptr<JsonArray> array;

	JsonValue(Type type_, std::wstring value_): type{type_} {
		value = std::move(value_);
	}
	JsonValue(std::unique_ptr<JsonObject>& object_): type{Type::Object} {
		object.swap(object_);
	}
	JsonValue(std::unique_ptr<JsonArray>& array_): type{Type::Array} {
		array.swap(array_);
	}

	bool GetStringValue(std::wstring_view key, std::wstring &value_) const {
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
	std::wstring_view doc;
	size_t index = 0;
	size_t lineStart = 0;
	unsigned lineno = 1;

	static constexpr bool IsWhiteSpace(int ch) noexcept {
		return ch <= ' ';
	}
	static constexpr bool IsControl(int ch) noexcept {
		return ch < ' ';
	}
	static constexpr bool IsWordChar(int ch) noexcept {
		return (ch >= '0' && ch <= '9')
			|| (ch >= 'a' && ch <= 'z')
			|| (ch >= 'A' && ch <= 'Z')
			|| ch == '+' || ch == '-'
			|| ch == '_' || ch == '.'
			|| ch >= 0x80;
	}

	void HandleLine(wchar_t ch) noexcept {
		if (ch == L'\n') {
			lineStart = index;
			++lineno;
		}
	}

	void ShowError(const char *prefix, int ch, size_t pos) noexcept {
		const unsigned column = static_cast<unsigned>(pos - lineStart + 1);
		char msg[1024];
		const int len = wsprintfA(msg, "%s unexpected character U+%04X at (%u, %u)\n", prefix, ch, lineno, column);
		WriteConsoleA(hStdError, msg, len, nullptr, nullptr);
		index = doc.length();
	}

	std::wstring ScanString() {
		std::wstring value;
		while (index < doc.length()) {
			const wchar_t ch = doc[index++];
			if (ch == L'\"') {
				break;
			}
			if (IsControl(ch)) {
				HandleLine(ch);
				break;
			}
			if (ch == L'\\' && index < doc.length()) {
				const wchar_t chNext = doc[index++];
				switch (chNext) {
				case L'\"':
				case L'\\':
				case L'/':
					value.push_back(chNext);
					break;
				case L'b':
					value.push_back(L'\b');
					break;
				case L'f':
					value.push_back(L'\f');
					break;
				case L'n':
					value.push_back(L'\n');
					break;
				case L'r':
					value.push_back(L'\r');
					break;
				case L't':
					value.push_back(L'\t');
					break;
				case L'u': {
					int digit = 0;
					uint32_t code = 0;
					for (size_t pos = index; pos < doc.length() && digit < 4; pos++, digit++) {
						const int hex = GetHexDigit(doc[pos]);
						if (hex < 0) {
							break;
						}
						code <<= 4;
						code |= hex;
					}
					if (digit == 4) {
						index += 4;
						value.push_back(static_cast<wchar_t>(code));
					} else {
						value.push_back(L'\\');
						value.push_back(L'u');
					}
				} break;
				default:
					value.push_back(L'\\');
					if (IsControl(chNext)) {
						HandleLine(ch);
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
			const wchar_t ch = doc[index++];
			switch (ch) {
			case L'[':
				return ParseArray();

			case L'{':
				return ParseObject();

			case L'\"': {
				const std::wstring value = ScanString();
				return std::make_unique<JsonValue>(JsonValue::Type::String, value);
			} break;

			default:
				if (IsWordChar(ch)) {
					const size_t start = index - 1;
					while (index < doc.length() && IsWordChar(doc[index])) {
						++index;
					}
					const std::wstring value(doc.substr(start, index - start));
					return std::make_unique<JsonValue>(JsonValue::Type::Number, value);
				}
				if (IsWhiteSpace(ch)) {
					HandleLine(ch);
				} else {
					ShowError(__func__, ch, index);
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
			const wchar_t ch = doc[index];
			switch (ch) {
			case L',':
				++index;
				break;

			case L']':
				++index;
				return std::make_unique<JsonValue>(array);

			default:
				if (IsWhiteSpace(ch)) {
					++index;
					HandleLine(ch);
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
		std::wstring key;
		bool hasKey = false;
		while (index < doc.length()) {
			const wchar_t ch = doc[index];
			switch (ch) {
			case L',':
				++index;
				break;

			case L':':
				++index;
				if (hasKey) {
					hasKey = false;
					auto value = ParseValue();
					if (value) {
						object->insert_or_assign(key, std::move(value));
					}
				}
				break;

			case L'}':
				++index;
				return std::make_unique<JsonValue>(object);

			default:
				if (IsWhiteSpace(ch)) {
					++index;
					HandleLine(ch);
				} else if (!hasKey) {
					const auto value = ParseValue();
					if (value && value->type < JsonValue::Type::Object) {
						key = value->value;
						hasKey = true;
					}
				} else {
					ShowError(__func__, ch, index);
				}
				break;
			}
		}
		return std::make_unique<JsonValue>(object);
	}

public:
	JsonParser(std::wstring_view doc_) noexcept : doc{doc_} {}
	JsonValuePtr Parse() {
		return ParseValue();
	}
};

std::vector<std::wstring> pathList;
std::atomic<uint32_t> pathIndex;
wchar_t clangTidyPath[MAX_PATH];
std::wstring commandLinePrefix;

inline bool PathIsFile(const wchar_t *path) noexcept {
	const DWORD attr = GetFileAttributesW(path);
	return (attr & FILE_ATTRIBUTE_DIRECTORY) == 0;
}

bool FindClangTidyPath() noexcept {
	wchar_t dir[MAX_PATH]{};
	GetModuleFileNameW(nullptr, dir, _countof(dir));
	wchar_t path[MAX_PATH]{};
	PathCombineW(path, dir, L"clang-tidy.exe");
	if (PathIsFile(path)) {
		memcpy(clangTidyPath, path, sizeof(path));
		return true;
	}

	if (SearchPathW(nullptr, L"clang-tidy.exe", nullptr, _countof(path), path, nullptr)) {
		GetFullPathNameW(path, _countof(clangTidyPath), clangTidyPath, nullptr);
		return true;
	}
	return false;
}

std::wstring FindCompileDatebase(std::wstring &directory) {
	wchar_t dir[MAX_PATH]{};
	if (!directory.empty()) {
		PathCombineW(dir, directory.c_str(), L"compile_commands.json");
		if (PathIsFile(dir)) {
			return dir;
		}
	}

	GetCurrentDirectoryW(_countof(dir), dir);
	while (true) {
		wchar_t path[MAX_PATH]{};
		PathCombineW(path, dir, L"compile_commands.json");
		if (PathIsFile(path)) {
			directory = dir;
			return path;
		}
		if (PathIsRootW(dir)) {
			break;
		}
		PathRemoveFileSpecW(dir);
	}
	return {};
}

bool ReadTextFile(const wchar_t *path, std::wstring &content) {
	HANDLE hFile = CreateFileW(path,
						GENERIC_READ,
						FILE_SHARE_READ | FILE_SHARE_WRITE,
						nullptr, OPEN_EXISTING,
						FILE_ATTRIBUTE_NORMAL,
						nullptr);
	if (hFile == INVALID_HANDLE_VALUE) {
		return false;
	}

	LARGE_INTEGER fileSize;
	fileSize.QuadPart = 0;
	if (!GetFileSizeEx(hFile, &fileSize) || fileSize.QuadPart == 0) {
		CloseHandle(hFile);
		return false;
	}

	const std::unique_ptr<char[]> doc = std::make_unique<char[]>(fileSize.QuadPart + 1);
	DWORD cbData = 0;
	const BOOL bReadSuccess = ReadFile(hFile, doc.get(), static_cast<DWORD>(fileSize.QuadPart), &cbData, nullptr);
	CloseHandle(hFile);
	if (!bReadSuccess || cbData == 0) {
		return false;
	}

	const char *data = doc.get();
	if (cbData >= 3 && data[0] == '\xEF' && data[1] == '\xBB' && data[2] == '\xBF') {
		// UTF-8 BOM
		data += 3;
		cbData -= 3;
	}

	content.resize(cbData + 1);
	cbData = MultiByteToWideChar(CP_UTF8, 0, data, cbData, content.data(), static_cast<int>(content.size()));
	content.resize(cbData);
	return cbData != 0;
}

void ParseCompileDatebase(const wchar_t *databasePath) {
	// https://clang.llvm.org/docs/JSONCompilationDatabase.html
	constexpr size_t minSize = sizeof(R"(["file":""])");
	std::wstring doc;
	ReadTextFile(databasePath, doc);
	if (doc.length() < minSize) {
		return;
	}

	JsonParser parser(doc);
	const auto database = parser.Parse();
	if (database && database->type == JsonValue::Type::Array && database->array) {
		std::wstring file;
		for (const auto &it : *database->array) {
			if (it && it->GetStringValue(L"file", file)) {
				if (PathIsRelativeW(file.c_str())) {
					std::wstring dir;
					if (it->GetStringValue(L"directory", dir)) {
						wchar_t path[MAX_PATH];
						PathCombineW(path, dir.c_str(), file.c_str());
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
		STARTUPINFOW startInfo{};
		startInfo.cb = sizeof(STARTUPINFO);
		startInfo.hStdInput = INVALID_HANDLE_VALUE;
		startInfo.hStdOutput = hStdOutput;
		startInfo.hStdError = hStdError;
		startInfo.dwFlags = STARTF_USESTDHANDLES;

		const std::wstring &path = pathList[index];
		std::wstring commandLine = commandLinePrefix + path + L"\"";
		if (!CreateProcessW(clangTidyPath, commandLine.data(),
			nullptr, nullptr, TRUE, 0, nullptr, nullptr,
			&startInfo, &procInfo)) {
			const std::wstring msg = L"run clang-tidy fail: " + commandLine + L"\n";
			WriteConsoleW(hStdError, msg.c_str(), static_cast<DWORD>(msg.length()), nullptr, nullptr);
		} else {
			WaitForSingleObject(procInfo.hProcess, INFINITE);
			CloseHandle(procInfo.hProcess);
			CloseHandle(procInfo.hThread);
		}
	}
}

}

int wmain(int argc, wchar_t *argv[]) {
	hStdOutput = GetStdHandle(STD_OUTPUT_HANDLE);
	hStdError = GetStdHandle(STD_ERROR_HANDLE);
	uint32_t jobCount = 1;
	std::wstring directory;
	for (int i = 1; i < argc; i++) {
		const wchar_t *arg = argv[i];
		if (arg[0] == L'-') {
			bool handled = false;
			switch (arg[1]) {
			case L'j':
				if (IsDigit(arg[2])) {
					handled = true;
					jobCount = wcstol(arg + 2, nullptr, 10);
				}
				break;
			}
			if (!handled) {
				commandLinePrefix += arg;
				commandLinePrefix += L' ';
			}
		}
	}

	if (!FindClangTidyPath()) {
		return 1;
	}

	const std::wstring path = FindCompileDatebase(directory);
	if (path.empty()) {
		return 2;
	}

	ParseCompileDatebase(path.c_str());
	if (pathList.empty()) {
		return 3;
	}

	commandLinePrefix += L" -p=\"" + directory + L"\" \"";
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
