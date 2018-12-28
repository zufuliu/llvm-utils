# LLVM Utils

## LLVM (8.0) for Visual Studio 2017

### Installation
Please download and install LLVM from http://llvm.org/builds/ or http://releases.llvm.org/.

Assume `VS_PATH` is your Visual Studio 2017 installation path (e.g: `C:\Program Files (x86)\Microsoft Visual Studio\2017\Community`),
please manually copy folder *LLVM v141* and *LLVM v141_xp* under `VS2017` to following target paths:

| Folder | Target Path |
|------|-------------|
|`VS2017\LLVM` | `%VS_PATH%\Common7\IDE\VC\VCTargets\LLVM\` |
|`VS2017\LLVM v141` | `%VS_PATH%\Common7\IDE\VC\VCTargets\Platforms\x64\PlatformToolsets\` |
|`VS2017\LLVM v141_xp` | `%VS_PATH%\Common7\IDE\VC\VCTargets\Platforms\x64\PlatformToolsets\` |
|`VS2017\LLVM v141` | `%VS_PATH%\Common7\IDE\VC\VCTargets\Platforms\Win32\PlatformToolsets\` |
|`VS2017\LLVM v141_xp` | `%VS_PATH%\Common7\IDE\VC\VCTargets\Platforms\Win32\PlatformToolsets\` |
|`VS2017\LLVM v141` | `%VS_PATH%\Common7\IDE\VC\VCTargets\Platforms\ARM64\PlatformToolsets\` |

or run `VS2017\install.bat` directly (which may require Administrator privilege. In Windows 8 or later, you can quickly open an elevated PowerShell prompt by File -> Open Windows PowerShell -> Open PowerShell as Administrator).

Notes:
* Old versions can be found at [release list](https://github.com/zufuliu/llvm-utils/tags), if you don't like to follow the following steps.
* If your LLVM version is not 8.0, please change `$(LLVMInstallDir)\lib\clang\8.0.0\` in *LLVM\LLVM.Common.targets* to appropriate value.
* If your VC compiler version is not `19.16.*` (VS2017 15.9, type `cl` in Command Prompt or find it in `%VS_PATH%\VC\Tools\MSVC`), please change `-fmsc-version=1916` in in *LLVM\LLVM.Common.targets* to appropriate value. A full list of `_MSC_VER` can be found at https://en.wikipedia.org/wiki/Microsoft_Visual_C%2B%2B#Internal_version_numbering, here is a brief list:

| Visual Studio Version | `_MSC_VER` |
|-----------------------|------------|
| Visual Studio 2017 15.9 | 1916 |
| Visual Studio 2017 15.8 | 1915 |
| Visual Studio 2017 15.7 | 1914 |
| Visual Studio 2017 15.6 | 1913 |
| Visual Studio 2017 15.5 | 1912 |
| Visual Studio 2017 15.3 | 1911 |
| Visual Studio 2017 15.0 | 1910 |
| Visual Studio 2015 14.0 | 1900 |

### Usage
Select *LLVM v141* or *LLVM v141_xp* as your project Platform Toolset.

### Install to AppVeyor Build Image

	git clone -q --branch=master https://github.com/zufuliu/llvm-utils.git c:\projects\llvm-utils
	CALL "c:\projects\llvm-utils\VS2017\install.bat" 1

Please note that LLVM 7.0.0 on AppVeyor doesn't support ARM64.

## LLVM Windows Symbolic Link Maker
The huge size of LLVM Windows installation can be reduced dramatically by using Windows symbolic link (see [mklink command](https://docs.microsoft.com/en-us/windows-server/administration/windows-commands/mklink).

### Usage
Just copy *llvm\llvm-link.bat* to LLVM installation path (such as `C:\Program Files\LLVM\`), and run it (which may require Administrator privilege).

## [License](../master/license.txt)

## Related Links
* [LLVM Extensions for Visual Studio 2017](https://marketplace.visualstudio.com/items?itemName=LLVMExtensions.llvm-toolchain) in Visual Studio Marketplace
* Original source for MSBuild

	svn co http://llvm.org/svn/llvm-project/llvm/trunk/tools/msbuild msbuild

* Outdated [LLVM for Visual Studio 2017](https://github.com/WubbaLubba/LlvmForVS2017) by @WubbaLubba
* [Failed to find MSBuild toolsets directory](https://bugs.llvm.org/show_bug.cgi?id=33672) in LLVM Bugzilla
