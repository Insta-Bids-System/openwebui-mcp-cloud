# 🧪 Local Testing Setup for MCP Tools

## Prerequisites
- Docker Desktop running on Windows
- Git Bash or WSL2 for better command compatibility
- Internet connection for pulling Docker images

## Step 1: Create Local Environment File

Create `.env.local` with these values:

```bash
# Core Services
POSTGRES_URL=postgresql://postgres:localpassword@postgres:5432/openwebui
REDIS_URL=redis://redis:6379/0
WEBUI_SECRET_KEY=local-secret-key-for-testing-only
OPENWEBUI_API_KEY=sk-local-testing-key

# MCP Configuration
MCP_API_KEY=local-mcp-api-key

# External APIs (use real keys for testing)
GITHUB_TOKEN=ghp_your_github_token_here
BRAVE_API_KEY=your_brave_api_key_here

# FileBrowser
FB_USERNAME=admin
FB_PASSWORD=admin123

# Optional (can add later)
SLACK_BOT_TOKEN=
DO_API_TOKEN=
```

## Step 2: Create Local Docker Compose

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
      - DATABASE_URL=${POSTGRES_URL}
      - WEBUI_SECRET_KEY=${WEBUI_SECRET_KEY}
      - REDIS_URL=${REDIS_URL}
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

  # Your custom MCP server
  mcp-server:
    build: ./mcp-server
    container_name: local-mcp-server
    environment:
      - OPENWEBUI_URL=http://open-webui:8080
      - OPENWEBUI_API_KEY=${OPENWEBUI_API_KEY}
      - REDIS_URL=${REDIS_URL}
    volumes:
      - ./data/workspace:/workspace
    networks:
      - local-ai-net

  # MCPO Bridge for OpenWebUI tools
  mcpo-openwebui:
    image: ghcr.io/open-webui/mcpo:main
    container_name: local-mcpo-openwebui
    ports:
      - "8101:8000"
    command: [
      "--host", "0.0.0.0", 
      "--port", "8000", 
      "--api-key", "${MCP_API_KEY}", 
      "--", 
      "python", "-m", "mcp_server"
    ]
    depends_on:
      - mcp-server
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

  # Brave Search MCP Tools
  mcpo-brave-search:
    image: ghcr.io/open-webui/mcpo:main
    container_name: local-mcpo-brave-search
    ports:
      - "8104:8000"
    command: [
      "--host", "0.0.0.0", 
      "--port", "8000", 
      "--api-key", "${MCP_API_KEY}", 
      "--", 
      "npx", "-y", "@modelcontextprotocol/server-brave-search"
    ]
    environment:
      - BRAVE_API_KEY=${BRAVE_API_KEY}
    networks:
      - local-ai-net

  # Memory MCP Tools
  mcpo-memory:
    image: ghcr.io/open-webui/mcpo:main
    container_name: local-mcpo-memory
    ports:
      - "8105:8000"
    command: [
      "--host", "0.0.0.0", 
      "--port", "8000", 
      "--api-key", "${MCP_API_KEY}", 
      "--", 
      "npx", "-y", "@modelcontextprotocol/server-memory"
    ]
    volumes:
      - ./data/memory:/data/memory
    networks:
      - local-ai-net

  # LiteLLM for Gemini
  litellm:
    image: ghcr.io/berriai/litellm:main-latest
    container_name: local-litellm
    ports:
      - "4000:4000"
    environment:
      - GEMINI_API_KEY=${GEMINI_API_KEY}
    command: [
      "--model", "gemini/gemini-1.5-flash",
      "--port", "4000"
    ]
    networks:
      - local-ai-net

networks:
  local-ai-net:
    driver: bridge

volumes:
  postgres-data:
```

## Step 3: Start Local Testing Environment

```bash
# Navigate to project directory
cd /path/to/openwebui-mcp-cloud

# Create data directories
mkdir -p data/{openwebui,workspace,memory}

# Start all services
docker-compose -f docker-compose.local.yml --env-file .env.local up -d

# Check status
docker ps

# View logs
docker-compose -f docker-compose.local.yml logs -f
```

## Step 4: Access Local Services

- **OpenWebUI**: http://localhost:8080
- **MCPO OpenWebUI**: http://localhost:8101/docs
- **MCPO GitHub**: http://localhost:8102/docs
- **MCPO Filesystem**: http://localhost:8103/docs
- **MCPO Brave Search**: http://localhost:8104/docs
- **MCPO Memory**: http://localhost:8105/docs

## Step 5: Test Each MCP Service

### Test OpenWebUI Tools (Port 8101)
```bash
# Check available tools
curl http://localhost:8101/openapi.json | jq '.paths | keys'

# Test health endpoint
curl -X POST http://localhost:8101/get_health \
  -H "Authorization: Bearer local-mcp-api-key" \
  -H "Content-Type: application/json" \
  -d '{}'
```

### Test GitHub Tools (Port 8102)
```bash
# List your repositories
curl -X POST http://localhost:8102/list_repositories \
  -H "Authorization: Bearer local-mcp-api-key" \
  -H "Content-Type: application/json" \
  -d '{"username": "your-github-username"}'
```

### Test Filesystem Tools (Port 8103)
```bash
# List workspace directory
curl -X POST http://localhost:8103/list_directory \
  -H "Authorization: Bearer local-mcp-api-key" \
  -H "Content-Type: application/json" \
  -d '{"path": "/workspace"}'
```

### Test Brave Search (Port 8104)
```bash
# Search for something
curl -X POST http://localhost:8104/search \
  -H "Authorization: Bearer local-mcp-api-key" \
  -H "Content-Type: application/json" \
  -d '{"query": "OpenWebUI MCP integration"}'
```

## Step 6: Configure OpenWebUI

1. Open http://localhost:8080
2. Create an account (auth disabled for local)
3. Go to **Settings → Connections → Add Connection**
4. Configure LiteLLM:
   - **Name**: Gemini
   - **Base URL**: http://litellm:4000/v1
   - **API Key**: sk-1234 (any value works)

5. Go to **Admin Panel → Tools → Add Connection**
6. Add each MCP service:

### For Each Service:
- **OpenWebUI Tools**: http://localhost:8101
- **GitHub Tools**: http://localhost:8102
- **Filesystem Tools**: http://localhost:8103
- **Brave Search**: http://localhost:8104
- **Memory Tools**: http://localhost:8105

**Settings for each:**
- **Auth Type**: Bearer
- **API Key**: local-mcp-api-key
- **Auto-append /openapi.json**: ON ✅

## 🔧 Troubleshooting

### Common Issues

#### 1. "Cannot connect to Docker daemon"
**Solution**: Make sure Docker Desktop is running

#### 2. Port already in use
**Solution**: 
```bash
# Check what's using the port (e.g., 8080)
netstat -ano | findstr :8080

# Or change the port in docker-compose.local.yml
ports:
  - "8081:8080"  # Use 8081 instead
```

#### 3. MCPO container exits immediately
**Check logs**:
```bash
docker logs local-mcpo-github
```

**Common fixes**:
- Ensure API keys are set in .env.local
- Check internet connection (needs to download npm packages)

#### 4. "Server Connection Error" in OpenWebUI
**Solutions**:
- Wait 30-60 seconds for all services to start
- Check MCPO is running: `docker ps | grep mcpo`
- Verify endpoints: `curl http://localhost:8101/openapi.json`

## 📝 Windows-Specific Commands

If using PowerShell instead of Git Bash:

```powershell
# Create directories
New-Item -ItemType Directory -Force -Path "data\openwebui", "data\workspace", "data\memory"

# Start services
docker-compose -f docker-compose.local.yml --env-file .env.local up -d

# View logs (use Select-String instead of grep)
docker ps | Select-String "mcpo"

# Test endpoint
Invoke-RestMethod -Uri "http://localhost:8101/openapi.json" -Method Get
```

## 🎯 Testing Checklist

- [ ] All containers running: `docker ps` shows 10+ containers
- [ ] OpenWebUI accessible: http://localhost:8080
- [ ] MCPO docs pages load: http://localhost:810X/docs
- [ ] Can add MCP connections in OpenWebUI
- [ ] Tools appear in Tools menu after adding
- [ ] Can execute a simple tool (e.g., get_health)

## 🧹 Cleanup

When done testing:

```bash
# Stop all services
docker-compose -f docker-compose.local.yml down

# Remove volumes (WARNING: deletes all data)
docker-compose -f docker-compose.local.yml down -v

# Remove all containers and networks
docker system prune -a
```

## 🚀 Next Steps

Once local testing is successful:

1. **Document what works**: Note any issues or changes needed
2. **Update production config**: Apply successful changes to docker-compose.production.yml
3. **Deploy to DigitalOcean**: Use the same configuration that worked locally
4. **Keep local as staging**: Use for testing new tools before production

## 📌 Quick Reference

### Service URLs
| Service | Local URL | Docs URL |
|---------|-----------|----------|
| OpenWebUI | http://localhost:8080 | - |
| MCPO OpenWebUI | http://localhost:8101 | http://localhost:8101/docs |
| MCPO GitHub | http://localhost:8102 | http://localhost:8102/docs |
| MCPO Filesystem | http://localhost:8103 | http://localhost:8103/docs |
| MCPO Brave Search | http://localhost:8104 | http://localhost:8104/docs |
| MCPO Memory | http://localhost:8105 | http://localhost:8105/docs |
| LiteLLM | http://localhost:4000 | http://localhost:4000/docs |

### Essential Commands
```bash
# Start everything
docker-compose -f docker-compose.local.yml --env-file .env.local up -d

# Check status
docker ps

# View specific service logs
docker logs -f local-mcpo-github

# Restart a service
docker-compose -f docker-compose.local.yml restart mcpo-github

# Stop everything
docker-compose -f docker-compose.local.yml down
```

Ready to test? Start with Step 1! 🎉
