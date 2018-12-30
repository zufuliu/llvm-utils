@ECHO OFF
SETLOCAL ENABLEEXTENSIONS

SET "EXIST_ON_ERROR=%~1"
SET SUCCESS=0

PUSHD %~dp0

@rem Visual Studio 2015
:TRY_2015
SET VCT_PATH=%ProgramFiles(x86)%\MSBuild\Microsoft.Cpp\v4.0\V140\Platforms
IF EXIST "%VCT_PATH%" GOTO FIND_2015
SET VCT_PATH=%ProgramFiles%\MSBuild\Microsoft.Cpp\v4.0\V140\Platforms
IF EXIST "%VCT_PATH%" GOTO FIND_2015
GOTO VC_NOT_FOUND

:FIND_2015
ECHO VCTargetsPath for Visual Studio 2015: %VCT_PATH%
XCOPY /Q /Y "LLVM" "%VCT_PATH%\..\LLVM\"
XCOPY /Q /Y "LLVM_v140" "%VCT_PATH%\x64\PlatformToolsets\LLVM_v140\"
XCOPY /Q /Y "LLVM_v140_xp" "%VCT_PATH%\x64\PlatformToolsets\LLVM_v140_xp\"
XCOPY /Q /Y "LLVM_v140" "%VCT_PATH%\Win32\PlatformToolsets\LLVM_v140\"
XCOPY /Q /Y "LLVM_v140_xp" "%VCT_PATH%\Win32\PlatformToolsets\LLVM_v140_xp\"
SET SUCCESS=1


:VC_NOT_FOUND
IF %SUCCESS% == 0 (
	ECHO Visual C++ 2015 NOT Installed.
	IF "%EXIST_ON_ERROR%" == "" PAUSE
)

POPD
ENDLOCAL
EXIST /B
