@echo off
echo Checking Docker services...
echo.
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo.
echo Testing OpenWebUI endpoint...
curl -s http://localhost:8080/health || echo OpenWebUI not ready yet
echo.
echo Testing MCPO endpoint...
curl -s http://localhost:8101/openapi.json > nul && echo MCPO is ready || echo MCPO not ready yet
echo.
echo If services show as "Up", proceed to http://localhost:8080
pause