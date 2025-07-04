@echo off
REM stop-local-testing.bat - Stop local MCP testing environment

echo ===================================
echo Stopping Local MCP Testing Environment
echo ===================================

REM Stop all services
docker-compose -f docker-compose.local.yml down

echo.
echo Services stopped.
echo.
echo To remove all data (volumes), run:
echo   docker-compose -f docker-compose.local.yml down -v
echo.
pause
