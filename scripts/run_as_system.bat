@echo off
setlocal enabledelayedexpansion

echo ========================================
echo    PrivilegeElevator - SYSTEM Mode
echo ========================================
echo.

:: Load configuration
python -c "import json; config = json.load(open('config.json')); print('Python: ' + config['paths']['python_executable']); print('PsExec: ' + config['paths']['psexec_path'])" > temp_config.txt
set /p PYTHON_PATH=<temp_config.txt
set PYTHON_PATH=!PYTHON_PATH:Python: =!
set /p PSEXEC_PATH=<temp_config.txt
set PSEXEC_PATH=!PSEXEC_PATH:PsExec: =!
del temp_config.txt

echo Using:
echo   Python: !PYTHON_PATH!
echo   PsExec: !PSEXEC_PATH!
echo.

if not exist "!PSEXEC_PATH!" (
    echo ❌ PsExec not found at: !PSEXEC_PATH!
    echo 💡 Please download from: https://docs.microsoft.com/en-us/sysinternals/downloads/pstools
    echo    and update config.json with the correct path
    pause
    exit /b 1
)

echo 🚀 Running PrivilegeElevator as SYSTEM...
"!PSEXEC_PATH!" -accepteula -s -i -w "%CD%" "!PYTHON_PATH!" "run.py" --demo

echo.
pause