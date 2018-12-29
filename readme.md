# LLVM Utils

## LLVM for Visual Studio 2017 and 2019

### Installation
Please download and install LLVM from http://llvm.org/builds/ or http://releases.llvm.org/.

Assume `VS_PATH` is your Visual Studio 2017 (or 2019) installation path (e.g: `C:\Program Files (x86)\Microsoft Visual Studio\2017\Community` or `C:\Program Files (x86)\Microsoft Visual Studio\2019\Preview`),
please manually copy folder *LLVM v141* and *LLVM v141_xp* under `VS2017` to following target paths:

| Folder | Target Path |
|------|-------------|
|`VS2017\LLVM` | `%VS_PATH%\Common7\IDE\VC\VCTargets\` |
|`VS2017\LLVM v141` | `%VS_PATH%\Common7\IDE\VC\VCTargets\Platforms\x64\PlatformToolsets\` |
|`VS2017\LLVM v141_xp` | `%VS_PATH%\Common7\IDE\VC\VCTargets\Platforms\x64\PlatformToolsets\` |
|`VS2017\LLVM v141` | `%VS_PATH%\Common7\IDE\VC\VCTargets\Platforms\Win32\PlatformToolsets\` |
|`VS2017\LLVM v141_xp` | `%VS_PATH%\Common7\IDE\VC\VCTargets\Platforms\Win32\PlatformToolsets\` |
|`VS2017\LLVM v141` | `%VS_PATH%\Common7\IDE\VC\VCTargets\Platforms\ARM64\PlatformToolsets\` |

or run `VS2017\install.bat` directly (may require Administrator privilege. In Windows 8 or later, you can quickly open an elevated PowerShell prompt by File -> Open Windows PowerShell -> Open PowerShell as Administrator).

Because `vswhere` doesn't print the installation path for Visual Studio 2019 Preview, please call the script with installation path, e.g: `CALL VS2017\install.bat "C:\Program Files (x86)\Microsoft Visual Studio\2019\Preview"` or call vsdevcmd.bat (or vcvarsall.bat, etc.) before this script.

### Usage
Select *LLVM v141* or *LLVM v141_xp* as your project's Platform Toolset.

### Install to AppVeyor Build Image

	curl -Ls -o "llvm-utils-master.zip" "https://github.com/zufuliu/llvm-utils/archive/master.zip"
	7z x -y "llvm-utils-master.zip" >NUL
	CALL "llvm-utils-master\VS2017\install.bat" 1

or

	git clone -q --depth=1 --branch=master https://github.com/zufuliu/llvm-utils.git c:\projects\llvm-utils
	CALL "c:\projects\llvm-utils\VS2017\install.bat" 1

Please note that LLVM 7.0.0 on AppVeyor doesn't support ARM64.

## LLVM for Visual Studio 2010, 2012, 2013 and 2015
Assume `MB_PATH` is the MSBuild path for Visual C++ (e.g.: `C:\Program Files (x86)\MSBuild\Microsoft.Cpp\v4.0` or `C:\Program Files\MSBuild\Microsoft.Cpp\v4.0`), please manually copy folder *LLVM v1x0* and *LLVM v1x0_xp* under `VS2015` to following target paths.

`VS2015\install.bat` (based on install script for [LLVM 6.0.1](http://releases.llvm.org/download.html#6.0.1)) can be used to install MSBuild script for Visual Studio 2010, 2012, 2013 and 2015. Install to AppVeyor build image is similar to VS2017.

### Visual Studio 2015
The Platform Toolset is *LLVM v140* and *LLVM v140_xp*.

| Folder | Target Path |
|------|-------------|
|`VS2017\LLVM` | `%MB_PATH%\V140\` |
|`VS2015\LLVM v140` | `%MB_PATH%\V140\Platforms\x64\PlatformToolsets\` |
|`VS2015\LLVM v140_xp` | `%MB_PATH%\V140\Platforms\x64\PlatformToolsets\` |
|`VS2015\LLVM v140` | `%MB_PATH%\V140\Platforms\Win32\PlatformToolsets\` |
|`VS2015\LLVM v140_xp` | `%MB_PATH%\V140\Platforms\Win32\PlatformToolsets\` |

### Visual Studio 2013
The Platform Toolset is *LLVM v120* and *LLVM v120_xp*.

| Folder | Target Path |
|------|-------------|
|`VS2017\LLVM` | `%MB_PATH%\v120\` |
|`VS2015\LLVM v120` | `%MB_PATH%\v120\Platforms\x64\PlatformToolsets\` |
|`VS2015\LLVM v120_xp` | `%MB_PATH%\v120\Platforms\x64\PlatformToolsets\` |
|`VS2015\LLVM v120` | `%MB_PATH%\v120\Platforms\Win32\PlatformToolsets\` |
|`VS2015\LLVM v120_xp` | `%MB_PATH%\v120\Platforms\Win32\PlatformToolsets\` |

### Visual Studio 2012
The Platform Toolset is *LLVM v110* and *LLVM v110_xp*.

| Folder | Target Path |
|------|-------------|
|`VS2017\LLVM` | `%MB_PATH%\v110\` |
|`VS2015\x64\LLVM v110` | `%MB_PATH%\v110\Platforms\x64\PlatformToolsets\` |
|`VS2015\x64\LLVM v110_xp` | `%MB_PATH%\v110\Platforms\x64\PlatformToolsets\` |
|`VS2015\Win32\LLVM v110` | `%MB_PATH%\v110\Platforms\Win32\PlatformToolsets\` |
|`VS2015\Win32\LLVM v110_xp` | `%MB_PATH%\v110\Platforms\Win32\PlatformToolsets\` |

### Visual Studio 2010
The Platform Toolset is *LLVM v100*.

| Folder | Target Path |
|------|-------------|
|`VS2017\LLVM` | `%MB_PATH%\` |
|`VS2015\x64\LLVM v100` | `%MB_PATH%\Platforms\x64\PlatformToolsets\` |
|`VS2015\Win32\LLVM v100` | `%MB_PATH%\Platforms\Win32\PlatformToolsets\` |

## LLVM Windows Symbolic Link Maker
The huge size of LLVM Windows installation can be reduced dramatically by using Windows symbolic link (see [mklink command](https://docs.microsoft.com/en-us/windows-server/administration/windows-commands/mklink).

### Usage
Just copy *llvm\llvm-link.bat* to LLVM installation path (e.g.: `C:\Program Files\LLVM\`), and run it (may require Administrator privilege).

## [License](../master/license.txt)

## Related Links
* [LLVM Extensions for Visual Studio 2017](https://marketplace.visualstudio.com/items?itemName=LLVMExtensions.llvm-toolchain) in Visual Studio Marketplace
* Original source for MSBuild

	svn co http://llvm.org/svn/llvm-project/llvm/trunk/tools/msbuild msbuild

* Outdated [LLVM for Visual Studio 2017](https://github.com/WubbaLubba/LlvmForVS2017) by @WubbaLubba
* [Failed to find MSBuild toolsets directory](https://bugs.llvm.org/show_bug.cgi?id=33672) in LLVM Bugzilla
