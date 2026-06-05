@echo off
setlocal
set DNF_INPUT_BACKEND=yijianshu
rem Optional: set YJS_DLL_PATH=D:\path\to\msdk64.dll
rem Optional: set YJS_VID=888C
rem Optional: set YJS_PID=88C1
python -m dnf.run_with_diagnostics
