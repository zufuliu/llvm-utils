# LLVM Utils

## LLVM (7.0) for Visual Studio 2017

### Installation
Please download and install LLVM from http://llvm.org/builds/ or http://releases.llvm.org/.

Assume `VS_PATH` is your Visual Studio 2017 installation path (such as `C:\Program Files (x86)\Microsoft Visual Studio 2017`),
please manually copy fold *LLVM v141* and *LLVM v141_xp* under `VS2017\Win32` and `VS2017\x64` to following target paths:

| Fold | Target Path |
|------|-------------|
|`VS2017\Win32` | `%VS_PATH%\Common7\IDE\VC\VCTargets\Platforms\Win32\PlatformToolsets\` |
|`VS2017\x64` | `%VS_PATH%\Common7\IDE\VC\VCTargets\Platforms\x64\PlatformToolsets\` |

or run `VS2017\install.bat` directly (witch may requre Administrator privilege).

Note: If your LLVM version is not 7.0, please change `$(LLVMInstallDir)\lib\clang\7.0\` in each *Toolset.props* to appropriate value.

### Usage
Select *LLVM v141* and *LLVM v141_xp* as your project Platform Toolset.

## LLVM Windows Symbolic Link Maker
The huge size of LLVM Windows installation can be reduced dramatically by use Windows symbolic link(see [mklink command](https://technet.microsoft.com/en-us/library/cc753194\(v=ws.11\).aspx)).

### Usage
Just copy *llvm-link.bat* to LLVM installation path (such as `C:\Program Files\LLVM\`), and run it.

## [License](http://llvm.org/releases/6.0.0/LICENSE.TXT)
