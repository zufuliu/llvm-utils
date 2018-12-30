@ECHO OFF
SETLOCAL ENABLEEXTENSIONS

IF EXIST "%~1" (
	SET "VS_PATH=%~1"
	SET "EXIST_ON_ERROR=%~2"
) ELSE (
	SET "EXIST_ON_ERROR=%~1"

	FOR /f "delims=" %%A IN (
	'"%ProgramFiles(x86)%\Microsoft Visual Studio\Installer\vswhere.exe" -property installationPath'
	) DO SET "VS_PATH=%%A"

	@rem VSINSTALLDIR is set by vsdevcmd_start.bat
	IF "%VS_PATH%" == "" SET "VS_PATH=%VSINSTALLDIR%"
)

SET VCT_PATH=%VS_PATH%\Common7\IDE\VC\VCTargets\Platforms
IF NOT EXIST "%VCT_PATH%" (
	ECHO Visual C++ 2017 or 2019 NOT Installed.
	IF "%EXIST_ON_ERROR%" == "" PAUSE
	ENDLOCAL
	EXIT /B
)

ECHO VCTargetsPath: %VCT_PATH%

PUSHD %~dp0

XCOPY /Q /Y "LLVM" "%VCT_PATH%\..\LLVM\"
XCOPY /Q /Y "LLVM_v141" "%VCT_PATH%\x64\PlatformToolsets\LLVM_v141\"
XCOPY /Q /Y "LLVM_v141_xp" "%VCT_PATH%\x64\PlatformToolsets\LLVM_v141_xp\"
XCOPY /Q /Y "LLVM_v141" "%VCT_PATH%\Win32\PlatformToolsets\LLVM_v141\"
XCOPY /Q /Y "LLVM_v141_xp" "%VCT_PATH%\Win32\PlatformToolsets\LLVM_v141_xp\"
XCOPY /Q /Y "LLVM_v141" "%VCT_PATH%\ARM64\PlatformToolsets\LLVM_v141\"

IF "%EXIST_ON_ERROR%" == "" PAUSE
POPD
ENDLOCAL
