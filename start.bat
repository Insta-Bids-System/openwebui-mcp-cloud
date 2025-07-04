@echo off
cls
echo ============================================
echo    OpenWebUI + MCP Tools Starter
echo ============================================
echo.

REM Check if Docker is running
docker version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Docker is not running!
    echo Please start Docker Desktop first.
    echo.
    pause
    exit /b 1
)

REM Check if .env exists
if not exist ".env" (
    echo ERROR: .env file not found!
    echo Please create .env file with your tokens.
    echo.
    echo Example .env:
    echo WEBUI_SECRET_KEY=my-secret-key
    echo MCP_API_KEY=local-mcp-key-for-testing
    echo GITHUB_TOKEN=ghp_YOUR_TOKEN_HERE
    echo.
    pause
    exit /b 1
)

echo Starting services...
docker-compose -f docker-compose.local.yml up -d

echo.
echo Waiting for services to start...
timeout /t 10 /nobreak >nul

echo.
echo ============================================
echo    Services Started Successfully!
echo ============================================
echo.
echo OpenWebUI:        http://localhost:8080
echo GitHub Tools:     http://localhost:8102
echo Filesystem Tools: http://localhost:8103
echo Workspace Files:  %cd%\data\workspace
echo.
echo Press any key to exit...
pause >nul
