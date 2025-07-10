@echo off
echo Checking MCP Tool Status...
echo.

echo GitHub MCP Server:
curl -X GET "http://localhost:8102/openapi.json" -H "Authorization: Bearer local-mcp-api-key" 2>nul | findstr /C:"list_repositories" >nul
if %errorlevel% equ 0 (
    echo [OK] GitHub tools are accessible
) else (
    echo [ERROR] Cannot access GitHub tools
)

echo.
echo Testing GitHub tool directly:
curl -X POST "http://localhost:8102/list_repositories" ^
  -H "Authorization: Bearer local-mcp-api-key" ^
  -H "Content-Type: application/json" ^
  -d "{\"username\": \"USER\"}"

echo.
pause
