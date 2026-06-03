@echo off
chcp 65001 >nul
set "report=%~dp0output\bug_reports\LATEST_BUG_REPORT.txt"
if exist "%report%" (
    start "" notepad "%report%"
) else (
    echo 还没有 BUG 报告。请先运行 run_dnf_with_diagnostics.bat。
    pause
)
