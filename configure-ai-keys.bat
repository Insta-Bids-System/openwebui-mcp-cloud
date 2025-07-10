@echo off
echo.
echo =====================================
echo API Key Configuration Helper
echo =====================================
echo.
echo This will help you add AI model API keys to your .env file
echo.

set /p OPENAI_KEY="Enter your OpenAI API key (or press Enter to skip): "
set /p GEMINI_KEY="Enter your Gemini API key (or press Enter to skip): "
set /p ANTHROPIC_KEY="Enter your Anthropic API key (or press Enter to skip): "

echo.
echo Updating .env file...

if not "%OPENAI_KEY%"=="" (
    powershell -Command "(Get-Content .env) -replace 'OPENAI_API_KEY=sk-YOUR_OPENAI_API_KEY_HERE.*', 'OPENAI_API_KEY=%OPENAI_KEY%' | Set-Content .env"
    echo ✓ OpenAI key updated
)

if not "%GEMINI_KEY%"=="" (
    powershell -Command "(Get-Content .env) -replace 'GEMINI_API_KEY=YOUR_GEMINI_API_KEY_HERE.*', 'GEMINI_API_KEY=%GEMINI_KEY%' | Set-Content .env"
    echo ✓ Gemini key updated
)

if not "%ANTHROPIC_KEY%"=="" (
    powershell -Command "(Get-Content .env) -replace 'ANTHROPIC_API_KEY=sk-ant-YOUR_ANTHROPIC_KEY_HERE.*', 'ANTHROPIC_API_KEY=%ANTHROPIC_KEY%' | Set-Content .env"
    echo ✓ Anthropic key updated
)

echo.
echo Configuration complete!
echo.
echo To apply changes, restart the services:
echo   docker-compose -f docker-compose.local.yml restart litellm
echo.
pause