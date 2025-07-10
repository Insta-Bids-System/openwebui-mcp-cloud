@echo off
REM Start Enhanced MCP Setup for Windows

echo =====================================
echo Starting Enhanced MCP Setup
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
if not exist "data\memory" mkdir data\memory

echo Data directories ready.
echo.

REM Pull or build images
echo Pulling/Building Docker images...
echo This may take a few minutes on first run...
echo.

docker-compose -f docker-compose.enhanced.yml build
docker-compose -f docker-compose.enhanced.yml pull

echo.
echo Starting services...
docker-compose -f docker-compose.enhanced.yml up -d

echo.
echo Waiting for services to start (30 seconds)...
timeout /t 30 /nobreak >nul

echo.
echo =====================================
echo Service Status:
echo =====================================
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo.
echo =====================================
echo Enhanced MCP Setup Complete!
echo =====================================
echo.
echo Service URLs:
echo   GitHub Wrapper (Enhanced):     http://localhost:8102
echo   Filesystem Wrapper (Enhanced): http://localhost:8107
echo   Filesystem MCP (Direct):       http://localhost:8104
echo   Search MCP:                    http://localhost:8105
echo   Memory MCP:                    http://localhost:8106
echo.
echo OpenWebUI Configuration:
echo   1. Open OpenWebUI in your browser
echo   2. Go to Settings - Tools
echo   3. Add these MCP servers:
echo      - GitHub: http://localhost:8102
echo      - Filesystem: http://localhost:8107
echo      - Search: http://localhost:8105
echo      - Memory: http://localhost:8106
echo.
echo To view logs: docker-compose -f docker-compose.enhanced.yml logs -f
echo To stop: docker-compose -f docker-compose.enhanced.yml down
echo.
pause