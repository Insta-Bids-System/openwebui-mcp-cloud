@echo off
echo.
echo 🔑 GitHub Token Configuration Helper
echo =====================================
echo.
echo Your current token appears to be invalid or expired.
echo.
echo To fix this:
echo.
echo 1. Go to: https://github.com/settings/tokens/new
echo.
echo 2. Create a new token with these permissions:
echo    ✓ repo (Full control of private repositories)
echo    ✓ read:user (Read user profile data)
echo    ✓ user:email (Access user email addresses)
echo.
echo 3. Copy your new token (starts with ghp_)
echo.
echo 4. Edit .env.local and replace this line:
echo    GITHUB_TOKEN=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
echo    with:
echo    GITHUB_TOKEN=your_actual_token_here
echo.
echo 5. Then run this command to restart GitHub MCP:
echo    docker-compose -f docker-compose.local.yml restart mcpo-github
echo.
echo Press any key to open GitHub token settings in your browser...
pause >nul
start https://github.com/settings/tokens/new
echo.
echo After updating your token, press any key to open .env.local...
pause >nul
notepad .env.local
echo.
pause
