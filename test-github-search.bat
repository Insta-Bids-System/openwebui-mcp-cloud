@echo off
echo Testing GitHub MCP Integration...
echo.

echo Searching for repositories with "openwebui"...
curl -X POST "http://localhost:8102/search_repositories" ^
  -H "Authorization: Bearer local-mcp-api-key" ^
  -H "Content-Type: application/json" ^
  -d "{\"query\": \"openwebui\", \"limit\": 5}"

echo.
pause
