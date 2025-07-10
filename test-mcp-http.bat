@echo off
echo.
echo 🧪 Testing MCP HTTP Server...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.7+ from https://python.org
    pause
    exit /b 1
)

REM Install requests if needed
echo 📦 Checking Python dependencies...
python -m pip install requests --quiet 2>nul

REM Run the test
echo.
echo 🚀 Running tests...
echo.
python test-mcp-http.py

echo.
pause
