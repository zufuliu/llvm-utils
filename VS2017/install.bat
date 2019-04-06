@ECHO OFF
SETLOCAL EnableExtensions EnableDelayedExpansion

SET "EXIT_ON_ERROR=%~1"
SET SUCCESS=0

PUSHD %~dp0

SET VSWHERE=%ProgramFiles(x86)%\Microsoft Visual Studio\Installer\vswhere.exe
@rem Visual Studio 2017
FOR /f "delims=" %%A IN ('"%VSWHERE%" -property installationPath -prerelease -version [15.0^,16.0^)') DO (
	SET VCT_PATH=%%A\Common7\IDE\VC\VCTargets\Platforms
	IF EXIST "!VCT_PATH!" CALL :SUB_VS2017 "!VCT_PATH!" 2017
)

@rem Visual Studio 2019
FOR /f "delims=" %%A IN ('"%VSWHERE%" -property installationPath -prerelease -version [16.0^,17.0^)') DO (
	SET VCT_PATH=%%A\MSBuild\Microsoft\VC\v160\Platforms
	IF EXIST "!VCT_PATH!" CALL :SUB_VS2019 "!VCT_PATH!"
	@rem Visual C++ 2017 v141 toolset
	SET VCT_PATH=%%A\MSBuild\Microsoft\VC\v150\Platforms
	IF EXIST "!VCT_PATH!" CALL :SUB_VS2017 "!VCT_PATH!" 2019
)

IF %SUCCESS% == 0 (
	ECHO Visual C++ 2017 or 2019 NOT Installed.
	IF "%EXIT_ON_ERROR%" == "" PAUSE
)

POPD
ENDLOCAL
EXIT /B


:SUB_VS2017
ECHO VCTargetsPath for Visual Studio %~2: %~1
XCOPY /Q /Y "LLVM" "%~1\..\LLVM\"
XCOPY /Q /Y "LLVM_v141" "%~1\x64\PlatformToolsets\LLVM_v141\"
XCOPY /Q /Y "LLVM_v141" "%~1\Win32\PlatformToolsets\LLVM_v141\"
XCOPY /Q /Y "LLVM_v141" "%~1\ARM64\PlatformToolsets\LLVM_v141\"
XCOPY /Q /Y "LLVM_v141_xp" "%~1\Win32\PlatformToolsets\LLVM_v141_xp\"
XCOPY /Q /Y "LLVM_v141_xp" "%~1\x64\PlatformToolsets\LLVM_v141_xp\"
SET SUCCESS=1
EXIT /B


:SUB_VS2019
ECHO VCTargetsPath for Visual Studio 2019: %~1
XCOPY /Q /Y "LLVM" "%~1\..\LLVM\"
XCOPY /Q /Y "LLVM_v142" "%~1\x64\PlatformToolsets\LLVM_v142\"
XCOPY /Q /Y "LLVM_v142" "%~1\Win32\PlatformToolsets\LLVM_v142\"
XCOPY /Q /Y "LLVM_v142" "%~1\ARM64\PlatformToolsets\LLVM_v142\"
SET SUCCESS=1
EXIT /B
