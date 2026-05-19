@echo off
cd /d "%~dp0"

python -c "import PyInstaller" >nul 2>nul
if errorlevel 1 (
    echo PyInstaller not found, installing...
    python -m pip install pyinstaller
    if errorlevel 1 (
        echo Failed to install PyInstaller.
        pause
        exit /b 1
    )
)

python -m PyInstaller ^
    --noconfirm ^
    --windowed ^
    --name "DNFBrushLauncher" ^
    --icon "dnf\res\app.ico" ^
    --add-data "dnf\res;dnf\res" ^
    --add-data "dnf\best.pt;dnf" ^
    --add-data "dnf\ds.pt;dnf" ^
    --add-data "dnf\ldd.pt;dnf" ^
    --add-data "dnf\pre.pt;dnf" ^
    --add-data "dnf\shzn.pt;dnf" ^
    --hidden-import win32timezone ^
    dnf\launcher.py

echo.
echo Build finished. Open dist\DNFBrushLauncher\DNFBrushLauncher.exe
pause
