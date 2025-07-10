@echo off
cls
echo ============================================
echo    Stopping OpenWebUI + MCP Tools
echo ============================================
echo.

echo Stopping all containers...
docker-compose -f docker-compose.local.yml down

echo.
echo All services stopped.
echo.
pause
