@ECHO OFF
@rem LLVM installation path
IF "%dp0%"=="" (SET LLVM=".\bin") ELSE (SET LLVM=%dp0%\bin)
@rem SET LLVM="C:\Program Files\LLVM\bin\"
IF NOT EXIST "%LLVM%" (
	ECHO LLVM not found.
	PAUSE
	EXIT /b
)

PUSHD "%LLVM%"

@rem delete MSVC runtime library
DEL api-ms*.dll
DEL concrt140.dll
DEL msvcp140.dll
DEL ucrtbase.dll
DEL vcruntime140*.dll

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

POPD

@rem Python lldb
PUSHD lib\site-packages\lldb

IF EXIST _lldb.pyd (
	DEL _lldb.pyd
	MKLINK _lldb.pyd ..\..\..\bin\liblldb.dll
)
@rem LLVM 14.0.0
IF EXIST _lldb.cp310-win_amd64.pyd (
	DEL _lldb.cp310-win_amd64.pyd
	MKLINK _lldb.cp310-win_amd64.pyd ..\..\..\bin\liblldb.dll
)
IF EXIST _lldb.cp310-win32.pyd (
	DEL _lldb.cp310-win32.pyd
	MKLINK _lldb.cp310-win32.pyd ..\..\..\bin\liblldb.dll
)

DEL lldb-argdumper.exe
MKLINK lldb-argdumper.exe ..\..\..\bin\lldb-argdumper.exe

POPD

@rem LLVM 8.0 and later no longer contains this folder
@rem MKDIR msbuild-bin
@rem PUSHD msbuild-bin
@rem
@rem DEL cl.exe
@rem MKLINK cl.exe ..\bin\clang.exe
@rem POPD

PAUSE
