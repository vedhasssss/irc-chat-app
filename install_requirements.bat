@echo off
title IRC Chat - Requirements Installer
echo ========================================
echo    IRC Chat Requirements Installer
echo ========================================
echo.

REM Check if Python is installed
echo [1/3] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from https://www.python.org/
    echo.
    pause
    exit /b 1
)
python --version
echo.

REM Check if pip is available
echo [2/3] Checking pip installation...
pip --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: pip is not installed
    echo Please reinstall Python with pip included
    echo.
    pause
    exit /b 1
)
pip --version
echo.

REM Install requirements
echo [3/3] Installing requirements from requirements.txt...
echo.
pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo ========================================
    echo    Installation FAILED!
    echo ========================================
    echo Please check the error messages above
    echo.
    pause
    exit /b 1
) else (
    echo.
    echo ========================================
    echo    Installation SUCCESSFUL!
    echo ========================================
    echo.
    echo All required packages have been installed.
    echo You can now run start_chat.bat to launch the application.
    echo.
    pause
)
