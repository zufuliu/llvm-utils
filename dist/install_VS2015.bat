@ECHO OFF
SETLOCAL ENABLEEXTENSIONS

SET "EXIT_ON_ERROR=%~1"
SET SUCCESS=0

PUSHD %~dp0

@rem Visual Studio 2015
SET VCT_PATH=%ProgramFiles(x86)%\MSBuild\Microsoft.Cpp\v4.0\v140\Platforms
IF EXIST "%VCT_PATH%" CALL :SUB_VS2015
SET VCT_PATH=%ProgramFiles%\MSBuild\Microsoft.Cpp\v4.0\v140\Platforms
IF EXIST "%VCT_PATH%" CALL :SUB_VS2015

IF %SUCCESS% == 0 (
	ECHO Visual C++ 2015 NOT Installed.
	IF "%EXIT_ON_ERROR%" == "" PAUSE
)

POPD
ENDLOCAL
EXIT /B


:SUB_VS2015
ECHO VCTargetsPath for Visual Studio 2015: %VCT_PATH%
XCOPY /Q /Y "LLVM" "%VCT_PATH%\..\LLVM\"
XCOPY /Q /Y "LLVM_v140" "%VCT_PATH%\x64\PlatformToolsets\LLVM_v140\"
XCOPY /Q /Y "LLVM_v140_xp" "%VCT_PATH%\x64\PlatformToolsets\LLVM_v140_xp\"
XCOPY /Q /Y "LLVM_v140" "%VCT_PATH%\Win32\PlatformToolsets\LLVM_v140\"
XCOPY /Q /Y "LLVM_v140_xp" "%VCT_PATH%\Win32\PlatformToolsets\LLVM_v140_xp\"
SET SUCCESS=1
EXIT /B
