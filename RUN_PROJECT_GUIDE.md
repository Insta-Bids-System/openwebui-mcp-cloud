# 🚀 OpenWebUI + MCP Tools - Complete Setup Guide

This guide will help you run the OpenWebUI + MCP Tools project from scratch.

## 📋 Prerequisites

1. **Windows 10/11** with PowerShell
2. **Docker Desktop** installed and running
3. **Git** installed
4. **GitHub Personal Access Token** (PAT)

## 🛠️ Step-by-Step Setup

### Step 1: Clone/Download the Project

```powershell
# Option A: If you have it on GitHub
git clone https://github.com/YOUR_USERNAME/openwebui-mcp-cloud.git
cd openwebui-mcp-cloud

# Option B: Create fresh directory
mkdir C:\Users\USER\Documents\openwebui-mcp-cloud
cd C:\Users\USER\Documents\openwebui-mcp-cloud
```

### Step 2: Create Directory Structure

```powershell
# Create required directories
mkdir -p data/workspace
mkdir -p data/openwebui
mkdir -p data/memory
mkdir -p mcp-server
```

### Step 3: Create Environment File

Create `.env` file with your credentials:

```env
# Basic configuration
WEBUI_SECRET_KEY=your-secret-key-here
MCP_API_KEY=your-mcp-api-key-here

# GitHub Personal Access Token (Required for GitHub tools)
GITHUB_TOKEN=ghp_YOUR_GITHUB_TOKEN_HERE

# Optional: External databases (leave commented for local)
# POSTGRES_URL=postgresql://user:pass@host:5432/openwebui
# REDIS_URL=redis://localhost:6379

# FileBrowser credentials
FB_USERNAME=admin
FB_PASSWORD=your-password-here

# Optional API Keys
OPENWEBUI_API_KEY=
DO_API_TOKEN=
BRAVE_API_KEY=
GEMINI_API_KEY=
```

### Step 4: Create Docker Compose File

Save this as `docker-compose.local.yml`:

```yaml
version: '3.9'

services:
  # Local PostgreSQL
  postgres:
    image: postgres:15-alpine
    container_name: local-postgres
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: localpassword
      POSTGRES_DB: openwebui
    volumes:
      - postgres-data:/var/lib/postgresql/data
    networks:
      - local-ai-net

  # Local Redis
  redis:
    image: redis:7-alpine
    container_name: local-redis
    networks:
      - local-ai-net

  # OpenWebUI
  open-webui:
    image: ghcr.io/open-webui/open-webui:main
    container_name: local-open-webui
    ports:
      - "8080:8080"
    environment:
      - DATABASE_URL=postgresql://postgres:localpassword@postgres:5432/openwebui
      - WEBUI_SECRET_KEY=${WEBUI_SECRET_KEY}
      - REDIS_URL=redis://redis:6379
      - ENABLE_COMMUNITY_SHARING=false
      - ENABLE_MESSAGE_RATING=true
      - DEFAULT_LOCALE=en
      - WEBUI_AUTH=false  # Disable auth for local testing
    volumes:
      - ./data/openwebui:/app/backend/data
    depends_on:
      - postgres
      - redis
    networks:
      - local-ai-net

  # Your custom MCP server (if you have one)
  mcp-server:
    build: ./mcp-server
    container_name: local-mcp-server
    environment:
      - OPENWEBUI_URL=http://open-webui:8080
      - OPENWEBUI_API_KEY=${OPENWEBUI_API_KEY}
      - REDIS_URL=redis://redis:6379
    volumes:
      - ./data/workspace:/workspace
    networks:
      - local-ai-net

  # GitHub MCP Tools
  mcpo-github:
    image: ghcr.io/open-webui/mcpo:main
    container_name: local-mcpo-github
    ports:
      - "8102:8000"
    command: [
      "--host", "0.0.0.0", 
      "--port", "8000", 
      "--api-key", "${MCP_API_KEY}", 
      "--", 
      "npx", "-y", "@modelcontextprotocol/server-github"
    ]
    environment:
      - GITHUB_PERSONAL_ACCESS_TOKEN=${GITHUB_TOKEN}
    networks:
      - local-ai-net

  # Filesystem MCP Tools
  mcpo-filesystem:
    image: ghcr.io/open-webui/mcpo:main
    container_name: local-mcpo-filesystem
    ports:
      - "8103:8000"
    command: [
      "--host", "0.0.0.0", 
      "--port", "8000", 
      "--api-key", "${MCP_API_KEY}", 
      "--", 
      "npx", "-y", "@modelcontextprotocol/server-filesystem", 
      "/workspace"
    ]
    volumes:
      - ./data/workspace:/workspace
    networks:
      - local-ai-net

networks:
  local-ai-net:
    driver: bridge

volumes:
  postgres-data:
```

### Step 5: Create MCP Server (Optional)

If you have a custom MCP server, create `mcp-server/Dockerfile`:

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "-m", "mcp_server"]
```

### Step 6: Start the Project

```powershell
# Pull latest images
docker-compose -f docker-compose.local.yml pull

# Start all services
docker-compose -f docker-compose.local.yml up -d

# Check if everything is running
docker-compose -f docker-compose.local.yml ps
```

### Step 7: Initialize OpenWebUI

1. Open browser to http://localhost:8080
2. Create admin account (first user becomes admin)
3. Go to Settings → Account → API Keys
4. Generate new API key
5. Copy the API key

### Step 8: Update Configuration with API Key

```powershell
# Add the API key to your .env file
# Edit .env and add:
# OPENWEBUI_API_KEY=sk-YOUR-GENERATED-KEY

# Restart MCP server if you have one
docker-compose -f docker-compose.local.yml restart mcp-server
```

### Step 9: Register MCP Tools in OpenWebUI

1. Go to Settings → Tools
2. Add GitHub Tools:
   - API Base URL: `http://localhost:8102`
   - Bearer Token: (your MCP_API_KEY from .env)
3. Add Filesystem Tools:
   - API Base URL: `http://localhost:8103`
   - Bearer Token: (your MCP_API_KEY from .env)

### Step 10: Verify Everything Works

Test in OpenWebUI chat:
- Filesystem: "Create a file test.txt with content 'Hello MCP'"
- GitHub: "Search for Python repositories with more than 100 stars"

## 🔧 Common Issues & Solutions

### Issue 1: Containers not starting
```powershell
# Check Docker is running
docker version

# Check logs
docker-compose -f docker-compose.local.yml logs
```

### Issue 2: GitHub tools not working
- Ensure GITHUB_TOKEN is set in .env
- Token needs repo, workflow permissions
- Restart mcpo-github container after adding token

### Issue 3: Files not persisting
- Check volume mounts in docker-compose
- Ensure ./data/workspace directory exists
- Files are saved in: C:\Users\USER\Documents\openwebui-mcp-cloud\data\workspace

## 🛑 Stopping the Project

```powershell
# Stop all containers
docker-compose -f docker-compose.local.yml down

# Stop and remove volumes (WARNING: Deletes all data)
docker-compose -f docker-compose.local.yml down -v
```

## 📦 Backup Your Configuration

```powershell
# Create backup directory
mkdir backup

# Copy important files
copy .env backup\
copy docker-compose.local.yml backup\
xcopy /E data\workspace backup\workspace\
```

## 🚀 Quick Start Script

Save as `start-project.ps1`:

```powershell
Write-Host "Starting OpenWebUI + MCP Tools..." -ForegroundColor Cyan

# Check if Docker is running
$dockerRunning = docker version 2>$null
if (-not $dockerRunning) {
    Write-Host "Docker is not running! Please start Docker Desktop." -ForegroundColor Red
    exit 1
}

# Check if .env exists
if (-not (Test-Path .env)) {
    Write-Host ".env file not found! Please create it first." -ForegroundColor Red
    exit 1
}

# Start services
Write-Host "Starting services..." -ForegroundColor Yellow
docker-compose -f docker-compose.local.yml up -d

# Wait for services
Write-Host "Waiting for services to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Check status
docker-compose -f docker-compose.local.yml ps

Write-Host "`nServices started!" -ForegroundColor Green
Write-Host "OpenWebUI: http://localhost:8080" -ForegroundColor Cyan
Write-Host "GitHub Tools: http://localhost:8102/openapi.json" -ForegroundColor Cyan
Write-Host "Filesystem Tools: http://localhost:8103/openapi.json" -ForegroundColor Cyan
```

## 📋 Checklist for Running Again

- [ ] Docker Desktop is running
- [ ] .env file exists with all tokens
- [ ] docker-compose.local.yml is present
- [ ] data/workspace directory exists
- [ ] Run: `docker-compose -f docker-compose.local.yml up -d`
- [ ] Access: http://localhost:8080
- [ ] Register tools in Settings → Tools
- [ ] Test with sample commands

That's it! Your AI-powered development environment with GitHub integration is ready! 🎉
