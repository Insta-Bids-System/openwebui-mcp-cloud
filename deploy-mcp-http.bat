@echo off
echo.
echo 🚀 Deploying fixed MCP server with HTTP integration...
echo.

REM Check if we're in the correct directory
if not exist "docker-compose.yml" (
    echo ❌ Error: docker-compose.yml not found. Please run from project root.
    exit /b 1
)

REM Stop any existing MCP server containers
echo 🛑 Stopping any existing MCP server...
docker-compose -f docker-compose.mcp-only.yml stop mcpo-openwebui 2>nul
docker-compose -f docker-compose.mcp-only.yml rm -f mcpo-openwebui 2>nul

REM Build the new HTTP server
echo.
echo 🔨 Building MCP HTTP server...
docker-compose -f docker-compose.mcp-http.yml build

REM Start the HTTP server
echo.
echo 🚀 Starting MCP HTTP server...
docker-compose -f docker-compose.mcp-http.yml up -d

REM Wait for it to be ready
echo.
echo ⏳ Waiting for server to be ready...
timeout /t 10 /nobreak >nul

REM Test the health endpoint
echo.
echo 🔍 Testing health endpoint...
curl -s http://localhost:8101/health

REM Test the OpenAPI endpoint
echo.
echo.
echo 📋 Checking OpenAPI endpoint...
curl -s http://localhost:8101/openapi.json | findstr "title"

echo.
echo.
echo ✅ MCP HTTP server deployed!
echo.
echo 📌 Next steps:
echo 1. Add to OpenWebUI at Settings -^> Tools
echo    - API Base URL: http://localhost:8101
echo    - Bearer Token: %MCP_API_KEY%
echo    - Enable 'Auto-append /openapi.json'
echo.
echo 2. Test with: 'List all users in OpenWebUI'
echo.
echo 3. View logs: docker logs -f local-mcp-server-http
echo.
pause
