@echo off
echo 🌞 Solar & Wind Energy Generation Dashboard
echo ==================================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.8 or higher
    pause
    exit /b 1
)

REM Check if we're in the right directory
if not exist "app.py" (
    echo ❌ app.py not found
    echo Please run this script from the project root directory
    pause
    exit /b 1
)

REM Run the launcher script
python run_dashboard.py

pause