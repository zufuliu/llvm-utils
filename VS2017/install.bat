@ECHO OFF

FOR /f "delims=" %%A IN (
'"%ProgramFiles(x86)%\Microsoft Visual Studio\Installer\vswhere.exe" -property installationPath'
) DO SET "VS_PATH=%%A"

SET VCT_PATH=%VS_PATH%\Common7\IDE\VC\VCTargets\Platforms
IF NOT EXIST "%VCT_PATH%" (
	ECHO Visual C++ 2017 NOT Installed.
	PAUSE
	EXIT /B
)

ECHO VCTargetsPath: %VCT_PATH%

XCOPY /Y "LLVM" "%VCT_PATH%\..\LLVM\"
XCOPY /Y "x64\LLVM v141" "%VCT_PATH%\x64\PlatformToolsets\LLVM v141\"
XCOPY /Y "x64\LLVM v141_xp" "%VCT_PATH%\x64\PlatformToolsets\LLVM v141_xp\"
XCOPY /Y "Win32\LLVM v141" "%VCT_PATH%\Win32\PlatformToolsets\LLVM v141\"
XCOPY /Y "Win32\LLVM v141_xp" "%VCT_PATH%\Win32\PlatformToolsets\LLVM v141_xp\"

PAUSE
