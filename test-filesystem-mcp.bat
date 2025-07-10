@echo off
echo Testing Filesystem MCP for local operations...
echo.

echo Creating a test file in workspace:
curl -X POST "http://localhost:8103/write_file" ^
  -H "Authorization: Bearer local-mcp-api-key" ^
  -H "Content-Type: application/json" ^
  -d "{\"path\": \"/workspace/test-file.txt\", \"content\": \"Hello from MCP!\"}"

echo.
echo.
echo Listing workspace directory:
curl -X POST "http://localhost:8103/list_directory" ^
  -H "Authorization: Bearer local-mcp-api-key" ^
  -H "Content-Type: application/json" ^
  -d "{\"path\": \"/workspace\"}"

echo.
pause
