@echo off
REM Stop Enhanced MCP Setup for Windows

echo =====================================
echo Stopping Enhanced MCP Setup
echo =====================================
echo.

docker-compose -f docker-compose.enhanced.yml down

echo.
echo All services stopped.
echo.
pause