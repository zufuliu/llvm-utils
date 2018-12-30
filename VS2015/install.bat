@ECHO OFF
SETLOCAL ENABLEEXTENSIONS

SET "EXIT_ON_ERROR=%~1"
SET SUCCESS=0

PUSHD %~dp0

@rem Visual Studio 2015
:TRY_2015
SET VCT_PATH=%ProgramFiles(x86)%\MSBuild\Microsoft.Cpp\v4.0\V140\Platforms
IF EXIST "%VCT_PATH%" GOTO FIND_2015
SET VCT_PATH=%ProgramFiles%\MSBuild\Microsoft.Cpp\v4.0\V140\Platforms
IF EXIST "%VCT_PATH%" GOTO FIND_2015
GOTO TRY_2013

:FIND_2015
ECHO VCTargetsPath for Visual Studio 2015: %VCT_PATH%
XCOPY /Q /Y "..\VS2017\LLVM" "%VCT_PATH%\..\LLVM\"
XCOPY /Q /Y "LLVM_v140" "%VCT_PATH%\x64\PlatformToolsets\LLVM_v140\"
XCOPY /Q /Y "LLVM_v140_xp" "%VCT_PATH%\x64\PlatformToolsets\LLVM_v140_xp\"
XCOPY /Q /Y "LLVM_v140" "%VCT_PATH%\Win32\PlatformToolsets\LLVM_v140\"
XCOPY /Q /Y "LLVM_v140_xp" "%VCT_PATH%\Win32\PlatformToolsets\LLVM_v140_xp\"
SET SUCCESS=1

@rem Visual Studio 2013
:TRY_2013
SET VCT_PATH=%ProgramFiles(x86)%\MSBuild\Microsoft.Cpp\v4.0\V120\Platforms
IF EXIST "%VCT_PATH%" GOTO FIND_2013
SET VCT_PATH=%ProgramFiles%\MSBuild\Microsoft.Cpp\v4.0\V120\Platforms
IF EXIST "%VCT_PATH%" GOTO FIND_2013
GOTO TRY_2012

:FIND_2013
ECHO VCTargetsPath for Visual Studio 2013: %VCT_PATH%
XCOPY /Q /Y "..\VS2017\LLVM" "%VCT_PATH%\..\LLVM\"
XCOPY /Q /Y "LLVM_v120" "%VCT_PATH%\x64\PlatformToolsets\LLVM_v120\"
XCOPY /Q /Y "LLVM_v120_xp" "%VCT_PATH%\x64\PlatformToolsets\LLVM_v120_xp\"
XCOPY /Q /Y "LLVM_v120" "%VCT_PATH%\Win32\PlatformToolsets\LLVM_v120\"
XCOPY /Q /Y "LLVM_v120_xp" "%VCT_PATH%\Win32\PlatformToolsets\LLVM_v120_xp\"
SET SUCCESS=1

@rem Visual Studio 2012
:TRY_2012
SET VCT_PATH=%ProgramFiles(x86)%\MSBuild\Microsoft.Cpp\v4.0\V110\Platforms
IF EXIST "%VCT_PATH%" GOTO FIND_2012
SET VCT_PATH=%ProgramFiles%\MSBuild\Microsoft.Cpp\v4.0\V110\Platforms
IF EXIST "%VCT_PATH%" GOTO FIND_2012
GOTO TRY_2010

:FIND_2012
ECHO VCTargetsPath for Visual Studio 2012: %VCT_PATH%
XCOPY /Q /Y "..\VS2017\LLVM" "%VCT_PATH%\..\LLVM\"
XCOPY /Q /Y "x64\LLVM_v110" "%VCT_PATH%\x64\PlatformToolsets\LLVM_v110\"
XCOPY /Q /Y "x64\LLVM_v110_xp" "%VCT_PATH%\x64\PlatformToolsets\LLVM_v110_xp\"
XCOPY /Q /Y "Win32\LLVM_v110" "%VCT_PATH%\Win32\PlatformToolsets\LLVM_v110\"
XCOPY /Q /Y "Win32\LLVM_v110_xp" "%VCT_PATH%\Win32\PlatformToolsets\LLVM_v110_xp\"
SET SUCCESS=1

@rem Visual Studio 2010
:TRY_2010
SET VCT_PATH=%ProgramFiles(x86)%\MSBuild\Microsoft.Cpp\v4.0\Platforms
IF EXIST "%VCT_PATH%" GOTO FIND_2010
SET VCT_PATH=%ProgramFiles%\MSBuild\Microsoft.Cpp\v4.0\Platforms
IF EXIST "%VCT_PATH%" GOTO FIND_2010
GOTO VC_NOT_FOUND

:FIND_2010
ECHO VCTargetsPath for Visual Studio 2010: %VCT_PATH%
XCOPY /Q /Y "..\VS2017\LLVM" "%VCT_PATH%\..\LLVM\"
XCOPY /Q /Y "x64\LLVM_v100" "%VCT_PATH%\x64\PlatformToolsets\LLVM_v100\"
XCOPY /Q /Y "Win32\LLVM_v100" "%VCT_PATH%\Win32\PlatformToolsets\LLVM_v100\"
XCOPY /Q /Y "x64\LLVM_v90" "%VCT_PATH%\x64\PlatformToolsets\LLVM_v90\"
XCOPY /Q /Y "Win32\LLVM_v90" "%VCT_PATH%\Win32\PlatformToolsets\LLVM_v90\"
SET SUCCESS=1

:VC_NOT_FOUND

IF %SUCCESS% == 0 (
	ECHO Visual C++ 2015, 2013, 2012 or 2010 NOT Installed.
	IF "%EXIT_ON_ERROR%" == "" PAUSE
)

POPD
ENDLOCAL
EXIT /B
