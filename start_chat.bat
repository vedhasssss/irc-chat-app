@echo off
title IRC Chat Launcher
echo ========================================
echo    Starting IRC Chat Application
echo ========================================
echo.
echo Starting server...
start "IRC Server" cmd /k "cd /d %~dp0server && python app.py"
timeout /t 2 /nobreak >nul
echo.
echo Starting client...
start "IRC Client" cmd /k "cd /d %~dp0client && python client.py"
echo.
echo ========================================
echo    IRC Chat Started!
echo ========================================
echo.
echo Server is running in one window
echo Client is running in another window
echo.
echo You can close this window now.
echo.
pause
