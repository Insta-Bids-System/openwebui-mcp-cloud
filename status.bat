@echo off
cls
echo ============================================
echo    OpenWebUI + MCP Tools Status
echo ============================================
echo.

echo Container Status:
echo -----------------
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | findstr "local-"

echo.
echo Quick Tests:
echo ------------
echo.

echo 1. Testing OpenWebUI...
curl -s -o nul -w "   OpenWebUI: %%{http_code}\n" http://localhost:8080/health 2>nul || echo    OpenWebUI: Not responding

echo.
echo 2. Testing GitHub Tools...
curl -s -o nul -w "   GitHub Tools: %%{http_code}\n" http://localhost:8102/openapi.json 2>nul || echo    GitHub Tools: Not responding

echo.
echo 3. Testing Filesystem Tools...
curl -s -o nul -w "   Filesystem Tools: %%{http_code}\n" http://localhost:8103/openapi.json 2>nul || echo    Filesystem Tools: Not responding

echo.
echo ============================================
echo.
echo If all show 200, everything is working!
echo.
pause
