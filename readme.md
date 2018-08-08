# LLVM Utils

## LLVM (8.0) for Visual Studio 2017

### Installation
Please download and install LLVM from http://llvm.org/builds/ or http://releases.llvm.org/.

Assume `VS_PATH` is your Visual Studio 2017 installation path (such as `C:\Program Files (x86)\Microsoft Visual Studio 2017`),
please manually copy fold *LLVM v141* and *LLVM v141_xp* under `VS2017\Win32` and `VS2017\x64` to following target paths:

| Fold | Target Path |
|------|-------------|
|`VS2017\Win32` | `%VS_PATH%\Common7\IDE\VC\VCTargets\Platforms\Win32\PlatformToolsets\` |
|`VS2017\x64` | `%VS_PATH%\Common7\IDE\VC\VCTargets\Platforms\x64\PlatformToolsets\` |

or run `VS2017\install.bat` directly (witch may require Administrator privilege. In Windows 8 or later, you can quickly open an elevated PowerShell prompt by File -> Open Windows PowerShell -> Open PowerShell as Administrator).

Note:
* LLVM 8.0 installer no longer create the *msbuild-bin* folder (which previously contains *cl.exe*) in it's installation directory, please create it manually or use the following *llvm-link.bat* to create it.
* Old versions can be found at [release list](https://github.com/zufuliu/llvm-utils/tags), if you don't like to follow the following steps.
* If your LLVM version is not 8.0, please change `$(LLVMInstallDir)\lib\clang\8.0.0\` in each *Toolset.props* to appropriate value.
* If your VC compiler version is not `19.14.*` (type `cl` in Command Prompt or find it in `%VS_PATH%\VC\Tools\MSVC`), please change `-fmsc-version=1914` in in each *Toolset.props* to appropriate value. A full list of `_MSC_VER` can be found at https://en.wikipedia.org/wiki/Microsoft_Visual_C%2B%2B#Internal_version_numbering, here is a brief list:

| Visual Studio Version | `_MSC_VER` |
|-----------------------|------------|
| Visual Studio 2015 14.0 | 1900 |
| Visual Studio 2017 15.0 | 1910 |
| Visual Studio 2017 15.3 | 1911 |
| Visual Studio 2017 15.5 | 1912 |
| Visual Studio 2017 15.6 | 1913 |
| Visual Studio 2017 15.7 | 1914 |

### Usage
Select *LLVM v141* and *LLVM v141_xp* as your project Platform Toolset.

## LLVM Windows Symbolic Link Maker
The huge size of LLVM Windows installation can be reduced dramatically by use Windows symbolic link (see [mklink command](https://docs.microsoft.com/en-us/windows-server/administration/windows-commands/mklink).

### Usage
Just copy *llvm-link.bat* to LLVM installation path (such as `C:\Program Files\LLVM\`), and run it.

## [License](http://llvm.org/releases/6.0.0/LICENSE.TXT)
