@echo off
echo Enabling Gemini API support...
echo.

REM Check if .env exists
if not exist .env (
    echo Error: .env file not found!
    echo Please run: copy .env.local .env
    pause
    exit /b 1
)

REM Add Gemini API key to .env if not already there
findstr /C:"GEMINI_API_KEY" .env >nul
if errorlevel 1 (
    echo.>> .env
    echo # Gemini API Key>> .env
    echo GEMINI_API_KEY=YOUR_GEMINI_API_KEY_HERE>> .env
    echo Added Gemini API key to .env
) else (
    echo Gemini API key already in .env
)

echo.
echo Now you need to:
echo 1. Edit docker-compose.yml
echo 2. Uncomment the litellm service (remove # from lines)
echo 3. Run: docker-compose up -d
echo.
echo Then in OpenWebUI:
echo - Go to Settings - Connections - OpenAI-Compatible
echo - API Base URL: http://localhost:4000/v1
echo - API Key: any-string-here
echo.
pause