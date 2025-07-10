@echo off
echo.
echo =====================================
echo OpenWebUI + MCP Tools Status Check
echo =====================================
echo.

echo Checking services...
echo.

echo OpenWebUI (http://localhost:8080):
curl -s -o nul -w "Status: %%{http_code}\n" http://localhost:8080

echo.
echo MCP Services:
echo - OpenWebUI Tools (8101): 
curl -s -o nul -w "  Status: %%{http_code}\n" http://localhost:8101/openapi.json

echo - GitHub (8103): 
curl -s -o nul -w "  Status: %%{http_code}\n" http://localhost:8103/openapi.json

echo - Filesystem (8104): 
curl -s -o nul -w "  Status: %%{http_code}\n" http://localhost:8104/openapi.json

echo - Search (8105): 
curl -s -o nul -w "  Status: %%{http_code}\n" http://localhost:8105/openapi.json

echo - Memory (8106): 
curl -s -o nul -w "  Status: %%{http_code}\n" http://localhost:8106/openapi.json

echo.
pause