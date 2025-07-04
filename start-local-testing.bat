@echo off
REM start-local-testing.bat - Start local MCP testing environment

echo ===================================
echo Starting Local MCP Testing Environment
echo ===================================

REM Check if Docker is running
docker version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Docker is not running!
    echo Please start Docker Desktop first.
    pause
    exit /b 1
)

REM Create data directories
echo Creating data directories...
if not exist "data\openwebui" mkdir "data\openwebui"
if not exist "data\workspace" mkdir "data\workspace"
if not exist "data\memory" mkdir "data\memory"

REM Check if .env.local exists
if not exist ".env.local" (
    echo ERROR: .env.local file not found!
    echo Please create .env.local from .env.template first.
    echo.
    echo Example:
    echo   copy .env.template .env.local
    echo   notepad .env.local
    pause
    exit /b 1
)

REM Pull latest images
echo.
echo Pulling latest Docker images...
docker pull ghcr.io/open-webui/open-webui:main
docker pull ghcr.io/open-webui/mcpo:main
docker pull postgres:15-alpine
docker pull redis:7-alpine

REM Start services
echo.
echo Starting services...
docker-compose -f docker-compose.local.yml --env-file .env.local up -d

REM Wait for services to start
echo.
echo Waiting for services to start (30 seconds)...
timeout /t 30 /nobreak >nul

REM Check service status
echo.
echo ===================================
echo Service Status:
echo ===================================
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo.
echo ===================================
echo Local Testing URLs:
echo ===================================
echo OpenWebUI:        http://localhost:8080
echo MCPO OpenWebUI:   http://localhost:8101/docs
echo MCPO GitHub:      http://localhost:8102/docs
echo MCPO Filesystem:  http://localhost:8103/docs
echo MCPO Search:      http://localhost:8104/docs
echo MCPO Memory:      http://localhost:8105/docs
echo.
echo To view logs: docker-compose -f docker-compose.local.yml logs -f
echo To stop:      docker-compose -f docker-compose.local.yml down
echo.
pause
