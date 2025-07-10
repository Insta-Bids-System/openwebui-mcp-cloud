@echo off
REM Start OpenWebUI with MCP Tools

echo =====================================
echo Starting OpenWebUI with MCP Tools
echo =====================================
echo.

REM Check if Docker is running
docker version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Docker is not running!
    echo Please start Docker Desktop first.
    pause
    exit /b 1
)

REM Check if .env file exists
if not exist ".env" (
    echo ERROR: .env file not found!
    echo Please create .env file with your API keys first.
    pause
    exit /b 1
)

REM Create data directories if they don't exist
if not exist "data" mkdir data
if not exist "data\openwebui" mkdir data\openwebui
if not exist "data\workspace" mkdir data\workspace

echo Data directories ready.
echo.

REM Pull images
echo Pulling Docker images...
docker pull ghcr.io/open-webui/open-webui:main
docker pull ghcr.io/open-webui/mcpo:main

echo.
echo Starting services...
docker-compose -f docker-compose.working.yml up -d

echo.
echo Waiting for services to start (20 seconds)...
timeout /t 20 /nobreak >nul

echo.
echo =====================================
echo Service Status:
echo =====================================
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo.
echo =====================================
echo Setup Complete!
echo =====================================
echo.
echo Access URLs:
echo   OpenWebUI:    http://localhost:8080
echo   Filesystem:   http://localhost:8101/docs
echo   GitHub:       http://localhost:8102/docs
echo   Time:         http://localhost:8103/docs
echo.
echo To add MCP tools in OpenWebUI:
echo   1. Open http://localhost:8080
echo   2. Create an account (no email needed)
echo   3. Go to Settings - Tools
echo   4. Add these MCP servers:
echo      - Filesystem: http://localhost:8101
echo      - GitHub: http://localhost:8102
echo      - Time: http://localhost:8103
echo.
echo To view logs: docker-compose -f docker-compose.working.yml logs -f
echo To stop: docker-compose -f docker-compose.working.yml down
echo.
pause