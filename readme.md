# LLVM Utils

## LLVM for Visual Studio 2017 and 2019

### Installation
Please download and install LLVM from http://llvm.org/builds/ or http://releases.llvm.org/.

Assume `VS_PATH` is your Visual Studio 2017 (or 2019) installation path (e.g: `C:\Program Files (x86)\Microsoft Visual Studio\2017\Community` or `C:\Program Files (x86)\Microsoft Visual Studio\2019\Preview`),
please manually copy folder *LLVM v141* and *LLVM v141_xp* under `VS2017` to following target paths:

| Folder | Target Path |
|------|-------------|
|`VS2017\LLVM` | `%VS_PATH%\Common7\IDE\VC\VCTargets\LLVM\` |
|`VS2017\LLVM v141` | `%VS_PATH%\Common7\IDE\VC\VCTargets\Platforms\x64\PlatformToolsets\` |
|`VS2017\LLVM v141_xp` | `%VS_PATH%\Common7\IDE\VC\VCTargets\Platforms\x64\PlatformToolsets\` |
|`VS2017\LLVM v141` | `%VS_PATH%\Common7\IDE\VC\VCTargets\Platforms\Win32\PlatformToolsets\` |
|`VS2017\LLVM v141_xp` | `%VS_PATH%\Common7\IDE\VC\VCTargets\Platforms\Win32\PlatformToolsets\` |
|`VS2017\LLVM v141` | `%VS_PATH%\Common7\IDE\VC\VCTargets\Platforms\ARM64\PlatformToolsets\` |

or run `VS2017\install.bat` directly (may require Administrator privilege. In Windows 8 or later, you can quickly open an elevated PowerShell prompt by File -> Open Windows PowerShell -> Open PowerShell as Administrator).

### Usage
Select *LLVM v141* or *LLVM v141_xp* as your project Platform Toolset.

### Install to AppVeyor Build Image

	curl -Ls -o "llvm-utils-master.zip" "https://github.com/zufuliu/llvm-utils/archive/master.zip"
	7z x -y "llvm-utils-master.zip" >NUL
	CALL "llvm-utils-master\VS2017\install.bat" 1

or

	git clone -q --depth=1 --branch=master https://github.com/zufuliu/llvm-utils.git c:\projects\llvm-utils
	CALL "c:\projects\llvm-utils\VS2017\install.bat" 1

Please note that LLVM 7.0.0 on AppVeyor doesn't support ARM64.

## LLVM Windows Symbolic Link Maker
The huge size of LLVM Windows installation can be reduced dramatically by using Windows symbolic link (see [mklink command](https://docs.microsoft.com/en-us/windows-server/administration/windows-commands/mklink).

### Usage
Just copy *llvm\llvm-link.bat* to LLVM installation path (such as `C:\Program Files\LLVM\`), and run it (may require Administrator privilege).

## [License](../master/license.txt)

## Related Links
* [LLVM Extensions for Visual Studio 2017](https://marketplace.visualstudio.com/items?itemName=LLVMExtensions.llvm-toolchain) in Visual Studio Marketplace
* Original source for MSBuild

	svn co http://llvm.org/svn/llvm-project/llvm/trunk/tools/msbuild msbuild

* Outdated [LLVM for Visual Studio 2017](https://github.com/WubbaLubba/LlvmForVS2017) by @WubbaLubba
* [Failed to find MSBuild toolsets directory](https://bugs.llvm.org/show_bug.cgi?id=33672) in LLVM Bugzilla
