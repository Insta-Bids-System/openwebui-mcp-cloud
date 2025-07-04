# 🚀 Quick Start - OpenWebUI + MCP Tools

## Prerequisites
- Docker Desktop running
- GitHub Personal Access Token

## 1️⃣ One-Time Setup (5 minutes)

### Create `.env` file:
```env
WEBUI_SECRET_KEY=my-secret-key-123
MCP_API_KEY=local-mcp-key-for-testing
GITHUB_TOKEN=ghp_YOUR_GITHUB_TOKEN_HERE
FB_USERNAME=admin
FB_PASSWORD=admin123
```

### Get your GitHub token:
1. Go to: https://github.com/settings/tokens
2. Generate new token (classic)
3. Select scopes: `repo`, `workflow`
4. Copy token to `.env`

## 2️⃣ Start Everything (Every Time)

```powershell
# In your project directory:
cd C:\Users\USER\Documents\openwebui-mcp-cloud

# Start all services
docker-compose -f docker-compose.local.yml up -d

# Check status (all should be "Up")
docker ps
```

## 3️⃣ First-Time Configuration

1. **Open OpenWebUI**: http://localhost:8080
2. **Create account** (first user = admin)
3. **Generate API key**: Settings → Account → API Keys → Generate
4. **Add to .env**: `OPENWEBUI_API_KEY=sk-YOUR-KEY`
5. **Restart**: `docker-compose -f docker-compose.local.yml restart`

## 4️⃣ Register Tools in OpenWebUI

Go to Settings → Tools → Add:

### GitHub Tools:
- API Base URL: `http://localhost:8102`
- Bearer Token: `local-mcp-key-for-testing`

### Filesystem Tools:
- API Base URL: `http://localhost:8103`
- Bearer Token: `local-mcp-key-for-testing`

## 5️⃣ Test It Works

In chat, try:
- "Create a file test.txt with Hello World"
- "Search for Python repos with 100+ stars"

## 📁 Where Are My Files?

Your files are in: `C:\Users\USER\Documents\openwebui-mcp-cloud\data\workspace\`

## 🛑 Stop Everything

```powershell
docker-compose -f docker-compose.local.yml down
```

## 💾 Backup Your Work

```powershell
# Backup command
xcopy /E data backup_$(Get-Date -Format "yyyy-MM-dd") /I
```

## 🔥 Start Fresh (Nuclear Option)

```powershell
# WARNING: Deletes everything!
docker-compose -f docker-compose.local.yml down -v
rm -r data
mkdir data\workspace
```

---

## 🎯 Quick Troubleshooting

**Tools not working?**
1. Check GitHub token in .env
2. Restart containers
3. Re-register tools in UI

**Can't access OpenWebUI?**
1. Check Docker is running
2. Check port 8080 isn't used
3. Check firewall

**Files not saving?**
- Check `data\workspace` exists
- Check Docker volume mounts

## 🚀 Even Quicker Start

Save this as `quick-start.bat`:

```batch
@echo off
echo Starting OpenWebUI + MCP Tools...
docker-compose -f docker-compose.local.yml up -d
timeout /t 5
echo.
echo Ready! Open http://localhost:8080
echo.
pause
```

That's it! Run `quick-start.bat` anytime to start your AI dev environment! 🎉
