@echo off
chcp 65001 >nul
cd /d "%~dp0"
python -m dnf.bug_check
echo.
echo 检查完成。报告保存在 output\bug_reports。
pause
