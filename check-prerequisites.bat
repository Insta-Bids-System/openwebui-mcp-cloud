@echo off
REM check-prerequisites.bat - Check if all requirements are installed

echo ===================================
echo Checking Prerequisites
echo ===================================
echo.

set PREREQ_MET=1

REM Check Docker
echo Checking Docker...
docker --version >nul 2>&1
if %errorlevel% equ 0 (
    echo [✓] Docker is installed
    docker version --format "    Version: {{.Server.Version}}"
) else (
    echo [X] Docker is NOT installed
    echo     Download from: https://www.docker.com/products/docker-desktop/
    set PREREQ_MET=0
)

echo.

REM Check Docker running
docker ps >nul 2>&1
if %errorlevel% equ 0 (
    echo [✓] Docker daemon is running
) else (
    echo [X] Docker daemon is NOT running
    echo     Please start Docker Desktop
    set PREREQ_MET=0
)

echo.

REM Check Git
echo Checking Git...
git --version >nul 2>&1
if %errorlevel% equ 0 (
    echo [✓] Git is installed
    git --version
) else (
    echo [X] Git is NOT installed
    echo     Download from: https://git-scm.com/download/win
    set PREREQ_MET=0
)

echo.

REM Check PowerShell version
echo Checking PowerShell...
powershell -Command "$PSVersionTable.PSVersion.Major" >nul 2>&1
if %errorlevel% equ 0 (
    echo [✓] PowerShell is available
    powershell -Command "Write-Host '    Version:' $PSVersionTable.PSVersion"
) else (
    echo [?] PowerShell check failed
)

echo.

REM Check if project files exist
echo Checking project files...
if exist "docker-compose.local.yml" (
    echo [✓] docker-compose.local.yml found
) else (
    echo [X] docker-compose.local.yml NOT found
    set PREREQ_MET=0
)

if exist "mcp-server\Dockerfile" (
    echo [✓] MCP server directory found
) else (
    echo [X] MCP server directory NOT found
    set PREREQ_MET=0
)

echo.
echo ===================================

if %PREREQ_MET% equ 1 (
    echo All prerequisites met! Ready to start testing.
    echo.
    echo Next steps:
    echo 1. Copy .env.local.template to .env.local
    echo 2. Add your API keys to .env.local
    echo 3. Run start-local-testing.bat
) else (
    echo Some prerequisites are missing. Please install them first.
)

echo ===================================
echo.
pause
