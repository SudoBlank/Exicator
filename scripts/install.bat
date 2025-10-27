@echo off
echo ========================================
echo    PrivilegeElevator Installation
echo ========================================
echo.

echo 🔧 Installing Python dependencies...
python -m pip install -r requirements.txt

echo.
echo 🛠️  Running auto-setup...
python run.py --setup

echo.
echo 📋 Checking system compatibility...
python -c "from src.config_manager import config; config.validate_system()"

echo.
echo 🎉 Installation complete!
echo.
echo 📚 Next steps:
echo    1. python run.py --gui     (Launch GUI)
echo    2. python run.py --demo    (Run demo)
echo    3. python run.py --help    (See all options)
echo.
pause