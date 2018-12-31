@ECHO OFF
ECHO DON'T run this script (which will overwrite Visual Studio 2013 and 2015 Platform Toolsets), it's for my test only.
PAUSE

CD "%~dp0\..\VS2015"

@rem Visual Studio 2015
SET VCT_PATH=%ProgramFiles(x86)%\MSBuild\Microsoft.Cpp\v4.0\V140\Platforms
ECHO VCTargetsPath for Visual Studio 2015: %VCT_PATH%
XCOPY /Q /Y "..\VS2017\LLVM" "%VCT_PATH%\..\LLVM\"
XCOPY /Q /Y "LLVM_v140" "%VCT_PATH%\x64\PlatformToolsets\LLVM_v140\"
XCOPY /Q /Y "LLVM_v140_xp" "%VCT_PATH%\x64\PlatformToolsets\LLVM_v140_xp\"
XCOPY /Q /Y "LLVM_v140" "%VCT_PATH%\Win32\PlatformToolsets\LLVM_v140\"
XCOPY /Q /Y "LLVM_v140_xp" "%VCT_PATH%\Win32\PlatformToolsets\LLVM_v140_xp\"
@rem Make fake Visual Studio 2015 Platform Toolsets
XCOPY /Q /Y "LLVM_v140" "%VCT_PATH%\x64\PlatformToolsets\v140\"
XCOPY /Q /Y "LLVM_v140_xp" "%VCT_PATH%\x64\PlatformToolsets\v140_xp\"
XCOPY /Q /Y "LLVM_v140" "%VCT_PATH%\Win32\PlatformToolsets\v140\"
XCOPY /Q /Y "LLVM_v140_xp" "%VCT_PATH%\Win32\PlatformToolsets\v140_xp\"

@rem Visual Studio 2013
SET VCT_PATH=%ProgramFiles(x86)%\MSBuild\Microsoft.Cpp\v4.0\V120\Platforms
XCOPY /Q /Y "..\VS2017\LLVM" "%VCT_PATH%\..\LLVM\"
XCOPY /Q /Y "LLVM_v120" "%VCT_PATH%\x64\PlatformToolsets\LLVM_v120\"
XCOPY /Q /Y "LLVM_v120_xp" "%VCT_PATH%\x64\PlatformToolsets\LLVM_v120_xp\"
XCOPY /Q /Y "LLVM_v120" "%VCT_PATH%\Win32\PlatformToolsets\LLVM_v120\"
XCOPY /Q /Y "LLVM_v120_xp" "%VCT_PATH%\Win32\PlatformToolsets\LLVM_v120_xp\"
@rem Make fake Visual Studio 2013 Platform Toolsets
XCOPY /Q /Y "LLVM_v120" "%VCT_PATH%\x64\PlatformToolsets\v120\"
XCOPY /Q /Y "LLVM_v120_xp" "%VCT_PATH%\x64\PlatformToolsets\v120_xp\"
XCOPY /Q /Y "LLVM_v120" "%VCT_PATH%\Win32\PlatformToolsets\v120\"
XCOPY /Q /Y "LLVM_v120_xp" "%VCT_PATH%\Win32\PlatformToolsets\v120_xp\"

@rem Visual Studio 2012
SET VCT_PATH=%ProgramFiles(x86)%\MSBuild\Microsoft.Cpp\v4.0\V110\Platforms
ECHO VCTargetsPath for Visual Studio 2012: %VCT_PATH%
XCOPY /Q /Y "..\VS2017\LLVM" "%VCT_PATH%\..\LLVM\"
XCOPY /Q /Y "x64\LLVM_v110" "%VCT_PATH%\x64\PlatformToolsets\LLVM_v110\"
XCOPY /Q /Y "x64\LLVM_v110_xp" "%VCT_PATH%\x64\PlatformToolsets\LLVM_v110_xp\"
XCOPY /Q /Y "Win32\LLVM_v110" "%VCT_PATH%\Win32\PlatformToolsets\LLVM_v110\"
XCOPY /Q /Y "Win32\LLVM_v110_xp" "%VCT_PATH%\Win32\PlatformToolsets\LLVM_v110_xp\"

@rem Visual Studio 2010
SET VCT_PATH=%ProgramFiles(x86)%\MSBuild\Microsoft.Cpp\v4.0\Platforms
ECHO VCTargetsPath for Visual Studio 2010: %VCT_PATH%
XCOPY /Q /Y "..\VS2017\LLVM" "%VCT_PATH%\..\LLVM\"
XCOPY /Q /Y "x64\LLVM_v100" "%VCT_PATH%\x64\PlatformToolsets\LLVM_v100\"
XCOPY /Q /Y "Win32\LLVM_v100" "%VCT_PATH%\Win32\PlatformToolsets\LLVM_v100\"
XCOPY /Q /Y "x64\LLVM_v90" "%VCT_PATH%\x64\PlatformToolsets\LLVM_v90\"
XCOPY /Q /Y "Win32\LLVM_v90" "%VCT_PATH%\Win32\PlatformToolsets\LLVM_v90\"

CD %~dp0
PAUSE
