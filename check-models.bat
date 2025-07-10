@echo off
echo Checking OpenWebUI configuration...
echo.

REM Check if OpenWebUI can see the models
echo Testing OpenAI connection...
curl -X POST http://localhost:8080/api/auth/signin ^
  -H "Content-Type: application/json" ^
  -d "{\"email\":\"admin@example.com\",\"password\":\"admin\"}" ^
  -o auth_response.json

echo.
echo If you see models in the UI now, great!
echo If not, try these steps:
echo.
echo 1. Go to http://localhost:8080
echo 2. Login with your account
echo 3. Go to Settings - Connections
echo 4. Make sure you have:
echo    - OpenAI connection with your API key
echo    - LiteLLM connection at http://litellm:4000/v1
echo 5. Click Save
echo 6. Logout and login again
echo.
pause