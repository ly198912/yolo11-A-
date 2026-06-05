@echo off
chcp 65001 >nul
cd /d "%~dp0"
set DNF_INPUT_BACKEND=yijianshu
python -m dnf.run_with_diagnostics
echo.
echo 程序已结束。若出现 BUG，请把 output\bug_reports\LATEST_BUG_REPORT.txt 交给 AI。
pause
