@echo off
echo Testing LiteLLM Connection...
echo.

echo 1. Checking if LiteLLM is running...
docker ps | findstr litellm >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] LiteLLM container is running
) else (
    echo [ERROR] LiteLLM container is not running
    exit /b 1
)

echo.
echo 2. Testing LiteLLM API...
powershell -Command "try { $response = Invoke-RestMethod -Uri 'http://localhost:4000/v1/models' -Headers @{'Authorization'='Bearer sk-1234'}; Write-Host '[OK] LiteLLM API is responding'; Write-Host 'Available models:'; $response.data | ForEach-Object { Write-Host '  -' $_.id } } catch { Write-Host '[ERROR] Cannot connect to LiteLLM API' }"

echo.
echo 3. Testing model completion...
powershell -Command "try { $body = @{model='gemini/gemini-1.5-flash'; messages=@(@{role='user'; content='Say hello'})} | ConvertTo-Json; $response = Invoke-RestMethod -Uri 'http://localhost:4000/v1/chat/completions' -Method Post -Headers @{'Authorization'='Bearer sk-1234'; 'Content-Type'='application/json'} -Body $body; Write-Host '[OK] Model is working!'; Write-Host 'Response:' $response.choices[0].message.content } catch { Write-Host '[ERROR] Model test failed:' $_.Exception.Message }"

echo.
pause
