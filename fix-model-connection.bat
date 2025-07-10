@echo off
echo.
echo 🔧 Fixing OpenWebUI Model Configuration
echo ========================================
echo.

REM Check if .env.local exists
if not exist ".env.local" (
    echo ❌ Error: .env.local not found!
    echo Please run from the project root directory
    pause
    exit /b 1
)

echo 📝 Current Setup:
echo - OpenWebUI is trying to use Ollama models
echo - We need to configure it to use GPT models via LiteLLM
echo.

echo 🔑 Step 1: Add Your API Keys
echo.
echo Please add these to your .env.local file:
echo.
echo # OpenAI API Key (for GPT models)
echo OPENAI_API_KEY=sk-YOUR_OPENAI_API_KEY_HERE
echo.
echo # Gemini API Key (optional)
echo GEMINI_API_KEY=YOUR_GEMINI_API_KEY_HERE
echo.
echo Press any key to open .env.local in notepad...
pause >nul
notepad .env.local

echo.
echo 🚀 Step 2: Restart LiteLLM with Multi-Model Support
echo.

REM Stop current LiteLLM
echo Stopping current LiteLLM...
docker stop local-litellm 2>nul
docker rm local-litellm 2>nul

REM Start new LiteLLM with config
echo Starting LiteLLM with multi-model configuration...
docker-compose -f docker-compose.litellm-fix.yml up -d

echo.
echo ⏳ Waiting for LiteLLM to start (30 seconds)...
timeout /t 30 /nobreak >nul

echo.
echo 🔍 Checking LiteLLM status...
curl -s http://localhost:4000/health
echo.

echo.
echo ✅ Step 3: Configure OpenWebUI
echo.
echo 1. Open http://localhost:8080
echo 2. Go to Settings -^> Connections
echo 3. Remove any Ollama connections
echo 4. Add OpenAI API connection:
echo    - API Base URL: http://localhost:4000/v1
echo    - API Key: any-string-here
echo.
echo 5. Save and refresh the page
echo.
echo 📋 Available Models (if API keys are set):
echo - gpt-4
echo - gpt-4-turbo
echo - gpt-3.5-turbo
echo - gemini-pro
echo - gemini-1.5-flash
echo.
echo Press any key to open OpenWebUI...
pause >nul
start http://localhost:8080
echo.
pause
