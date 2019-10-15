@ECHO OFF

SETLOCAL ENABLEEXTENSIONS
SET "KEEP_DIST_FOLDER=%~1"
SET "MAKE_ZIP_ARCHIVE=%~2"
CD /D %~dp0
DEL /Q LLVM_VS*.zip

ECHO Visual Studio 2017 and 2019
RD /Q /S LLVM_VS2017
XCOPY /Q /Y ..\license.txt                 LLVM_VS2017\license.txt*
XCOPY /Q /Y ..\llvm\llvm-link.bat          LLVM_VS2017\llvm-link.bat*
XCOPY /Q /Y ..\clang\clang-cl-py3.diff     LLVM_VS2017\clang-cl-py3.diff*
XCOPY /Q /S /Y ..\VS2017                   LLVM_VS2017\
IF "%MAKE_ZIP_ARCHIVE%" == "" CALL :SUB_MAKE_ZIP LLVM_VS2017
IF "%KEEP_DIST_FOLDER%" == "" RD /Q /S LLVM_VS2017


ECHO Visual Studio 2010 to 2015
RD /Q /S LLVM_VS2010_2015
XCOPY /Q /Y ..\license.txt                 LLVM_VS2010_2015\license.txt*
XCOPY /Q /Y ..\llvm\llvm-link.bat          LLVM_VS2010_2015\llvm-link.bat*
XCOPY /Q /Y ..\clang\clang-cl-py3.diff     LLVM_VS2010_2015\clang-cl-py3.diff*
XCOPY /Q /Y ..\VS2017\LLVM                 LLVM_VS2010_2015\LLVM\
XCOPY /Q /S /Y ..\VS2015                   LLVM_VS2010_2015\
XCOPY /Q /Y install_VS2010_2015.bat        LLVM_VS2010_2015\install.bat*
IF "%MAKE_ZIP_ARCHIVE%" == "" CALL :SUB_MAKE_ZIP LLVM_VS2010_2015
IF "%KEEP_DIST_FOLDER%" == "" RD /Q /S LLVM_VS2010_2015


ECHO Visual Studio 2015
RD /Q /S LLVM_VS2015
XCOPY /Q /Y ..\license.txt                  LLVM_VS2015\license.txt*
XCOPY /Q /Y ..\llvm\llvm-link.bat           LLVM_VS2015\llvm-link.bat*
XCOPY /Q /Y ..\clang\clang-cl-py3.diff      LLVM_VS2015\clang-cl-py3.diff*
XCOPY /Q /Y ..\VS2017\LLVM                  LLVM_VS2015\LLVM\
XCOPY /Q /Y ..\VS2015\LLVM_v140             LLVM_VS2015\LLVM_v140\
XCOPY /Q /Y ..\VS2015\LLVM_v140_xp          LLVM_VS2015\LLVM_v140_xp\
XCOPY /Q /Y install_VS2015.bat              LLVM_VS2015\install.bat*
IF "%MAKE_ZIP_ARCHIVE%" == "" CALL :SUB_MAKE_ZIP LLVM_VS2015
IF "%KEEP_DIST_FOLDER%" == "" RD /Q /S LLVM_VS2015


ECHO Visual Studio 2013
RD /Q /S LLVM_VS2013
XCOPY /Q /Y ..\license.txt                  LLVM_VS2013\license.txt*
XCOPY /Q /Y ..\llvm\llvm-link.bat           LLVM_VS2013\llvm-link.bat*
XCOPY /Q /Y ..\clang\clang-cl-py3.diff      LLVM_VS2013\clang-cl-py3.diff*
XCOPY /Q /Y ..\VS2017\LLVM                  LLVM_VS2013\LLVM\
XCOPY /Q /Y ..\VS2015\LLVM_v120             LLVM_VS2013\LLVM_v120\
XCOPY /Q /Y ..\VS2015\LLVM_v120_xp          LLVM_VS2013\LLVM_v120_xp\
XCOPY /Q /Y install_VS2013.bat              LLVM_VS2013\install.bat*
IF "%MAKE_ZIP_ARCHIVE%" == "" CALL :SUB_MAKE_ZIP LLVM_VS2013
IF "%KEEP_DIST_FOLDER%" == "" RD /Q /S LLVM_VS2013


ECHO Visual Studio 2012
RD /Q /S LLVM_VS2012
XCOPY /Q /Y ..\license.txt                  LLVM_VS2012\license.txt*
XCOPY /Q /Y ..\llvm\llvm-link.bat           LLVM_VS2012\llvm-link.bat*
XCOPY /Q /Y ..\clang\clang-cl-py3.diff      LLVM_VS2012\clang-cl-py3.diff*
XCOPY /Q /Y ..\VS2017\LLVM                  LLVM_VS2012\LLVM\
XCOPY /Q /Y ..\VS2015\x64\LLVM_v110         LLVM_VS2012\x64\LLVM_v110\
XCOPY /Q /Y ..\VS2015\x64\LLVM_v110_xp      LLVM_VS2012\x64\LLVM_v110_xp\
XCOPY /Q /Y ..\VS2015\Win32\LLVM_v110       LLVM_VS2012\Win32\LLVM_v110\
XCOPY /Q /Y ..\VS2015\Win32\LLVM_v110_xp    LLVM_VS2012\Win32\LLVM_v110_xp\
XCOPY /Q /Y install_VS2012.bat              LLVM_VS2012\install.bat*
IF "%MAKE_ZIP_ARCHIVE%" == "" CALL :SUB_MAKE_ZIP LLVM_VS2012
IF "%KEEP_DIST_FOLDER%" == "" RD /Q /S LLVM_VS2012


ECHO Visual Studio 2010
RD /Q /S LLVM_VS2010
XCOPY /Q /Y ..\license.txt                  LLVM_VS2010\license.txt*
XCOPY /Q /Y ..\llvm\llvm-link.bat           LLVM_VS2010\llvm-link.bat*
XCOPY /Q /Y ..\clang\clang-cl-py3.diff      LLVM_VS2010\clang-cl-py3.diff*
XCOPY /Q /Y ..\VS2017\LLVM                  LLVM_VS2010\LLVM\
XCOPY /Q /Y ..\VS2015\x64\LLVM_v100         LLVM_VS2010\x64\LLVM_v100\
XCOPY /Q /Y ..\VS2015\x64\LLVM_v90          LLVM_VS2010\x64\LLVM_v90\
XCOPY /Q /Y ..\VS2015\Win32\LLVM_v100       LLVM_VS2010\Win32\LLVM_v100\
XCOPY /Q /Y ..\VS2015\Win32\LLVM_v90        LLVM_VS2010\Win32\LLVM_v90\
XCOPY /Q /Y install_VS2010.bat              LLVM_VS2010\install.bat*
IF "%MAKE_ZIP_ARCHIVE%" == "" CALL :SUB_MAKE_ZIP LLVM_VS2010
IF "%KEEP_DIST_FOLDER%" == "" RD /Q /S LLVM_VS2010

ENDLOCAL
EXIT /B

:SUB_MAKE_ZIP
7z a -tzip -mx9 "%~1.zip" "%~1" >NUL
EXIT /B
