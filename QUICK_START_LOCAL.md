# 🚀 Quick Start - Local MCP Testing

## Prerequisites Checklist
- [ ] Docker Desktop installed and running
- [ ] Git installed
- [ ] GitHub personal access token
- [ ] Brave Search API key (optional)

## 1️⃣ One-Time Setup (2 minutes)

```bash
# Clone the repo (if you haven't already)
git clone https://github.com/yourusername/openwebui-mcp-cloud.git
cd openwebui-mcp-cloud

# Create your environment file
copy .env.local.template .env.local
notepad .env.local

# Add your API keys:
# - GITHUB_TOKEN=ghp_your_token_here
# - BRAVE_API_KEY=your_key_here (optional)
```

## 2️⃣ Start Everything (1 click)

**Option A: Double-click `start-local-testing.bat`**

**Option B: PowerShell**
```powershell
.\start-local-testing.bat
```

## 3️⃣ Access OpenWebUI

1. Open http://localhost:8080
2. Create an account (no email needed)
3. You're ready!

## 4️⃣ Add MCP Tools

Go to **Admin Panel → Tools → Add Connection**

For each service, add:
- **URL**: `http://localhost:810X` (X = 1-5)
- **API Key**: `local-mcp-api-key`
- **Auto-append**: ON ✅

| Service | Port | URL |
|---------|------|-----|
| OpenWebUI Tools | 8101 | http://localhost:8101 |
| GitHub | 8102 | http://localhost:8102 |
| Filesystem | 8103 | http://localhost:8103 |
| Brave Search | 8104 | http://localhost:8104 |
| Memory | 8105 | http://localhost:8105 |

## 5️⃣ Test Tools

**PowerShell:**
```powershell
.\test-mcp-endpoints.ps1
```

## 🛑 Stop Everything

**Double-click `stop-local-testing.bat`**

## 🎯 Success Indicators

- ✅ All containers show "Up" status
- ✅ Can access http://localhost:8080
- ✅ MCPO docs pages load (http://localhost:810X/docs)
- ✅ Tools appear in OpenWebUI after adding
- ✅ Can execute tools from chat

## ⚡ Common Fixes

**Port conflict?**
```powershell
# Find what's using port 8080
netstat -ano | findstr :8080

# Change port in docker-compose.local.yml
ports:
  - "8081:8080"  # Use 8081 instead
```

**Container not starting?**
```powershell
# Check logs
docker logs local-mcpo-github

# Restart specific service
docker restart local-mcpo-github
```

**Tools not appearing?**
1. Wait 30 seconds after adding
2. Refresh OpenWebUI (F5)
3. Check connection: http://localhost:810X/openapi.json

---

Ready? Just run `start-local-testing.bat` and go! 🚀
