@rem assume llvm is the root path, see build-llvm.txt

@cd llvm
svn update

@cd projects
@cd compiler-rt
svn update
@cd ..\libcxx
svn update
@cd ..\libcxxabi
svn update
@cd ..\libunwind
svn update
@cd ..\openmp
svn update
@cd ..\parallel-libs
svn update

@cd ..\..\tools
@cd lld
svn update
@cd ..\lldb
svn update
@cd ..\polly
svn update
@cd ..\clang
svn update
@cd tools\extra
svn update

@pause
