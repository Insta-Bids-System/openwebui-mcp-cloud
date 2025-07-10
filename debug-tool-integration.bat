@echo off
echo Checking OpenWebUI Tool Integration...
echo.

echo 1. Testing if tools are registered in OpenWebUI:
powershell -Command "Invoke-RestMethod -Uri 'http://localhost:8080/api/tools' -Headers @{'Authorization'='Bearer sk-local-testing-key'} | ConvertTo-Json"

echo.
echo 2. Testing model capabilities:
powershell -Command "$body = @{model='gemini/gemini-1.5-flash'; messages=@(@{role='user'; content='What tools do you have access to?'})} | ConvertTo-Json; Invoke-RestMethod -Uri 'http://localhost:4000/v1/chat/completions' -Method Post -Headers @{'Authorization'='Bearer sk-1234'; 'Content-Type'='application/json'} -Body $body | ConvertTo-Json"

echo.
pause
