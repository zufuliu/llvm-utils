@ECHO OFF
@rem LLVM installation path
IF "%dp0%"=="" (SET LLVM=".\bin") ELSE (SET LLVM=%dp0%\bin)
@rem SET LLVM="C:\Program Files\LLVM\bin\"
IF NOT EXIST "%LLVM%" (
	ECHO LLVM not found.
	PAUSE
	EXIT /b
)

CD "%LLVM%"

@rem delete MSVC runtime library
DEL api-ms*.dll
DEL concrt140.dll
DEL msvcp140.dll
DEL ucrtbase.dll
DEL vcruntime140.dll

@rem make symbolic link
DEL clang++.exe
MKLINK clang++.exe clang.exe

DEL clang-cl.exe
MKLINK clang-cl.exe clang.exe

DEL clang-cpp.exe
MKLINK clang-cpp.exe clang.exe

DEL lld-link.exe
MKLINK lld-link.exe lld.exe

DEL ld.lld.exe
MKLINK ld.lld.exe lld.exe

DEL ld64.lld.exe
MKLINK ld64.lld.exe lld.exe

DEL wasm-ld.exe
MKLINK wasm-ld.exe lld.exe

DEL llvm-lib.exe
MKLINK llvm-lib.exe llvm-ar.exe

DEL llvm-ranlib.exe
MKLINK llvm-ranlib.exe llvm-ar.exe

@rem DEL libiomp5md.dll
@rem MKLINK libiomp5md.dll libomp.dll

CD ..\msbuild-bin

DEL cl.exe
MKLINK cl.exe ..\bin\clang.exe

PAUSE
