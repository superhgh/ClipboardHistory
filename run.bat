@echo off
cd /d "%~dp0"

if not exist "venv\Scripts\python.exe" (
    echo [ERROR] venv not found!
    pause
    exit /b 1
)

echo Starting Clipboard History...
echo.

"%~dp0venv\Scripts\python.exe" "%~dp0src\main.py"

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Exit code: %errorlevel%
    pause
)
