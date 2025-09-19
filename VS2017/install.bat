@ECHO OFF
SETLOCAL EnableExtensions EnableDelayedExpansion

SET "EXIT_ON_ERROR=%~1"
SET SUCCESS=0

PUSHD %~dp0

SET VSWHERE=%ProgramFiles(x86)%\Microsoft Visual Studio\Installer\vswhere.exe

@rem Visual Studio 2017
FOR /f "delims=" %%A IN ('"%VSWHERE%" -property installationPath -prerelease -version [15.0^,16.0^)') DO (
	SET VCT_PATH=%%A\Common7\IDE\VC\VCTargets\Platforms
	IF EXIST "!VCT_PATH!" CALL :SUB_VS2017 "!VCT_PATH!"
)

@rem Visual Studio 2017 Build Tools
FOR /f "delims=" %%A IN ('"%VSWHERE%" -products Microsoft.VisualStudio.Product.BuildTools -property installationPath -prerelease -version [15.0^,16.0^)') DO (
	SET VCT_PATH=%%A\Common7\IDE\VC\VCTargets\Platforms
	IF EXIST "!VCT_PATH!" CALL :SUB_VS2017 "!VCT_PATH!"
)

@rem Visual Studio 2019, 2022��2026
FOR /f "delims=" %%A IN ('"%VSWHERE%" -property installationPath -prerelease -version [16.0^,19.0^)') DO (
	@rem Visual C++ 2026 v145 toolset
	SET VCT_PATH=%%A\MSBuild\Microsoft\VC\v180\Platforms
	IF EXIST "!VCT_PATH!" CALL :SUB_VS2026 "!VCT_PATH!"
	@rem Visual C++ 2022 v143 toolset
	SET VCT_PATH=%%A\MSBuild\Microsoft\VC\v170\Platforms
	IF EXIST "!VCT_PATH!" CALL :SUB_VS2022 "!VCT_PATH!"
	@rem Visual C++ 2019 v142 toolset
	SET VCT_PATH=%%A\MSBuild\Microsoft\VC\v160\Platforms
	IF EXIST "!VCT_PATH!" CALL :SUB_VS2019 "!VCT_PATH!"
	@rem Visual C++ 2017 v141 toolset
	SET VCT_PATH=%%A\MSBuild\Microsoft\VC\v150\Platforms
	IF EXIST "!VCT_PATH!" CALL :SUB_VS2017 "!VCT_PATH!"
)

@rem Visual Studio 2019, 2022��2026 Build Tools
FOR /f "delims=" %%A IN ('"%VSWHERE%" -products Microsoft.VisualStudio.Product.BuildTools -property installationPath -prerelease -version [16.0^,19.0^)') DO (
	@rem Visual C++ 2026 v145 toolset
	SET VCT_PATH=%%A\MSBuild\Microsoft\VC\v180\Platforms
	IF EXIST "!VCT_PATH!" CALL :SUB_VS2026 "!VCT_PATH!"
	@rem Visual C++ 2022 v143 toolset
	SET VCT_PATH=%%A\MSBuild\Microsoft\VC\v170\Platforms
	IF EXIST "!VCT_PATH!" CALL :SUB_VS2022 "!VCT_PATH!"
	@rem Visual C++ 2019 v142 toolset
	SET VCT_PATH=%%A\MSBuild\Microsoft\VC\v160\Platforms
	IF EXIST "!VCT_PATH!" CALL :SUB_VS2019 "!VCT_PATH!"
	@rem Visual C++ 2017 v141 toolset
	SET VCT_PATH=%%A\MSBuild\Microsoft\VC\v150\Platforms
	IF EXIST "!VCT_PATH!" CALL :SUB_VS2017 "!VCT_PATH!"
)

IF %SUCCESS% == 0 (
	ECHO Visual C++ 2017, 2019 or 2022 NOT Installed.
	IF "%EXIT_ON_ERROR%" == "" PAUSE
)

POPD
ENDLOCAL
EXIT /B


:SUB_VS2017
ECHO VCTargetsPath for Visual Studio 2017: %~1
XCOPY /Q /Y "LLVM" "%~1\..\LLVM\"
XCOPY /Q /Y "LLVM_v141" "%~1\x64\PlatformToolsets\LLVM_v141\"
XCOPY /Q /Y "LLVM_v141" "%~1\Win32\PlatformToolsets\LLVM_v141\"
XCOPY /Q /Y "LLVM_v141" "%~1\ARM64\PlatformToolsets\LLVM_v141\"
XCOPY /Q /Y "LLVM_v141" "%~1\ARM\PlatformToolsets\LLVM_v141\"
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
XCOPY /Q /Y "LLVM_v142" "%~1\ARM\PlatformToolsets\LLVM_v142\"
SET SUCCESS=1
EXIT /B

:SUB_VS2022
ECHO VCTargetsPath for Visual Studio 2022: %~1
XCOPY /Q /Y "LLVM" "%~1\..\LLVM\"
XCOPY /Q /Y "LLVM_v143" "%~1\x64\PlatformToolsets\LLVM_v143\"
XCOPY /Q /Y "LLVM_v143" "%~1\Win32\PlatformToolsets\LLVM_v143\"
XCOPY /Q /Y "LLVM_v143" "%~1\ARM64\PlatformToolsets\LLVM_v143\"
XCOPY /Q /Y "LLVM_v143" "%~1\ARM\PlatformToolsets\LLVM_v143\"
SET SUCCESS=1
EXIT /B

:SUB_VS2026
ECHO VCTargetsPath for Visual Studio 2026: %~1
XCOPY /Q /Y "LLVM" "%~1\..\LLVM\"
XCOPY /Q /Y "LLVM_v145" "%~1\x64\PlatformToolsets\LLVM_v145\"
XCOPY /Q /Y "LLVM_v145" "%~1\Win32\PlatformToolsets\LLVM_v145\"
XCOPY /Q /Y "LLVM_v145" "%~1\ARM64\PlatformToolsets\LLVM_v145\"
SET SUCCESS=1
EXIT /B
