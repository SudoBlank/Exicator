@echo off
setlocal enabledelayedexpansion

echo ========================================
echo    PRIVILEGE ANALYZER GUI - SYSTEM LEVEL
echo ========================================
echo.

:: Set paths
set "SCRIPT_DIR=C:\Users\Aadi\OneDrive\Documents\Apps\Randomapps\exp"
set "PYTHON_EXE=C:\Users\Aadi\AppData\Local\Programs\Python\Python313\python.exe"
set "PSEXEC=C:\Tools\PsExec64.exe"
set "GUI_SCRIPT=%SCRIPT_DIR%\privilege_demo_gui.py"

:: Verify files
if not exist "%GUI_SCRIPT%" (
    echo ❌ GUI script not found!
    pause
    exit /b 1
)

echo 🚀 Launching Privilege Analyzer GUI as SYSTEM...
echo    This will show your 95.7%% success rate in a beautiful interface!
echo.

:: Run as SYSTEM
cd /d "%SCRIPT_DIR%"
"%PSEXEC%" -accepteula -s -i -w "%SCRIPT_DIR%" "%PYTHON_EXE%" "%GUI_SCRIPT%"

echo.
pause