@ECHO OFF
SETLOCAL ENABLEEXTENSIONS

SET "EXIT_ON_ERROR=%~1"
SET SUCCESS=0

PUSHD %~dp0

@rem Visual Studio 2010
:TRY_2010
SET VCT_PATH=%ProgramFiles(x86)%\MSBuild\Microsoft.Cpp\v4.0\Platforms
IF EXIST "%VCT_PATH%" GOTO FIND_2010
SET VCT_PATH=%ProgramFiles%\MSBuild\Microsoft.Cpp\v4.0\Platforms
IF EXIST "%VCT_PATH%" GOTO FIND_2010
GOTO VC_NOT_FOUND

:FIND_2010
ECHO VCTargetsPath for Visual Studio 2010: %VCT_PATH%
XCOPY /Q /Y "LLVM" "%VCT_PATH%\..\LLVM\"
XCOPY /Q /Y "x64\LLVM_v100" "%VCT_PATH%\x64\PlatformToolsets\LLVM_v100\"
XCOPY /Q /Y "Win32\LLVM_v100" "%VCT_PATH%\Win32\PlatformToolsets\LLVM_v100\"
XCOPY /Q /Y "x64\LLVM_v90" "%VCT_PATH%\x64\PlatformToolsets\LLVM_v90\"
XCOPY /Q /Y "Win32\LLVM_v90" "%VCT_PATH%\Win32\PlatformToolsets\LLVM_v90\"
SET SUCCESS=1


:VC_NOT_FOUND
IF %SUCCESS% == 0 (
	ECHO Visual C++ 2010 NOT Installed.
	IF "%EXIT_ON_ERROR%" == "" PAUSE
)

POPD
ENDLOCAL
EXIT /B
