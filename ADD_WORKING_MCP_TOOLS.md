# 🚀 Adding Working MCP Tools to Your Setup

## Current Status
✅ **Working**: OpenWebUI with 165 tools via MCPO on port 8101
❌ **Not Working**: GitHub (8102) and DigitalOcean (8103) - need proper MCP servers

## Step 1: Update Docker Compose with Working MCP Servers

Replace the broken MCPO configurations with working ones:

```yaml
  # === Working MCP Tools ===
  
  # GitHub Tools (Port 8102)
  mcpo-github:
    image: ghcr.io/open-webui/mcpo:main
    container_name: mcpo-github
    restart: unless-stopped
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
      - ai-hub-net

  # Filesystem Tools (Port 8103) - More useful than DO for now
  mcpo-filesystem:
    image: ghcr.io/open-webui/mcpo:main
    container_name: mcpo-filesystem
    restart: unless-stopped
    ports:
      - "8103:8000"
    command: [
      "--host", "0.0.0.0", 
      "--port", "8000", 
      "--api-key", "${MCP_API_KEY}", 
      "--", 
      "npx", "-y", "@modelcontextprotocol/server-filesystem", 
      "/data/workspace"
    ]
    volumes:
      - /data/workspace:/data/workspace
    networks:
      - ai-hub-net
      
  # Brave Search Tools (Port 8104)
  mcpo-brave-search:
    image: ghcr.io/open-webui/mcpo:main
    container_name: mcpo-brave-search
    restart: unless-stopped
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
      - ai-hub-net

  # Memory/Knowledge Tools (Port 8105)
  mcpo-memory:
    image: ghcr.io/open-webui/mcpo:main
    container_name: mcpo-memory
    restart: unless-stopped
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
      - /data/memory:/data/memory
    networks:
      - ai-hub-net
```

## Step 2: Add Required Environment Variables

Add these to your `.env.production` file:

```bash
# Existing (you already have these)
MCP_API_KEY=your-secure-key-here
OPENWEBUI_API_KEY=sk-5c4c8bbe20364a7ca261a778f9f19273

# New additions
GITHUB_TOKEN=ghp_your_github_personal_access_token
BRAVE_API_KEY=your_brave_search_api_key
```

### How to Get API Keys:
- **GitHub Token**: https://github.com/settings/tokens (create with repo, read:user permissions)
- **Brave Search API**: https://api.search.brave.com/app/keys (free tier available)

## Step 3: Deploy the Updated Services

From your DigitalOcean droplet:

```bash
# SSH into your droplet
ssh root@159.65.36.162

# Navigate to project
cd /root/ai-hub-cloud

# Pull latest MCPO image
docker pull ghcr.io/open-webui/mcpo:main

# Update docker-compose.production.yml with new services
nano docker-compose.production.yml

# Start the new services
docker-compose -f docker-compose.production.yml up -d

# Check all services are running
docker-compose -f docker-compose.production.yml ps

# View logs if needed
docker-compose -f docker-compose.production.yml logs -f mcpo-github
```

## Step 4: Add Tools to OpenWebUI

For each MCP service, add it in OpenWebUI:

1. Go to **Admin Panel → Tools → Add Connection**

2. Add each service:

### GitHub Tools (Port 8102)
- **API Base URL**: `http://159.65.36.162:8102`
- **API Key**: Your MCP_API_KEY
- **Auto-append /openapi.json**: ON ✅

### Filesystem Tools (Port 8103)
- **API Base URL**: `http://159.65.36.162:8103`
- **API Key**: Your MCP_API_KEY
- **Auto-append /openapi.json**: ON ✅

### Brave Search Tools (Port 8104)
- **API Base URL**: `http://159.65.36.162:8104`
- **API Key**: Your MCP_API_KEY
- **Auto-append /openapi.json**: ON ✅

### Memory Tools (Port 8105)
- **API Base URL**: `http://159.65.36.162:8105`
- **API Key**: Your MCP_API_KEY
- **Auto-append /openapi.json**: ON ✅

## Step 5: Test Each Tool Category

### Test GitHub Tools:
```bash
curl -X POST http://159.65.36.162:8102/list_repositories \
  -H "Authorization: Bearer YOUR_MCP_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"username": "your-github-username"}'
```

### Test Filesystem Tools:
```bash
curl -X POST http://159.65.36.162:8103/list_directory \
  -H "Authorization: Bearer YOUR_MCP_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"path": "/data/workspace"}'
```

### Test Search Tools:
```bash
curl -X POST http://159.65.36.162:8104/search \
  -H "Authorization: Bearer YOUR_MCP_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "OpenWebUI MCP integration"}'
```

## Additional Recommended MCP Tools

### 1. Slack Integration (Port 8106)
```yaml
  mcpo-slack:
    image: ghcr.io/open-webui/mcpo:main
    container_name: mcpo-slack
    restart: unless-stopped
    ports:
      - "8106:8000"
    command: [
      "--host", "0.0.0.0", 
      "--port", "8000", 
      "--api-key", "${MCP_API_KEY}", 
      "--", 
      "npx", "-y", "@modelcontextprotocol/server-slack"
    ]
    environment:
      - SLACK_BOT_TOKEN=${SLACK_BOT_TOKEN}
    networks:
      - ai-hub-net
```

### 2. PostgreSQL Tools (Port 8107)
```yaml
  mcpo-postgres:
    image: ghcr.io/open-webui/mcpo:main
    container_name: mcpo-postgres
    restart: unless-stopped
    ports:
      - "8107:8000"
    command: [
      "--host", "0.0.0.0", 
      "--port", "8000", 
      "--api-key", "${MCP_API_KEY}", 
      "--", 
      "npx", "-y", "@modelcontextprotocol/server-postgres", 
      "${POSTGRES_URL}"
    ]
    networks:
      - ai-hub-net
```

## Troubleshooting Common Issues

### Issue: "Server Connection Error" in OpenWebUI
**Solution**: 
- Check MCPO is running: `docker ps | grep mcpo`
- Test endpoint: `curl http://159.65.36.162:810X/openapi.json`
- Check logs: `docker logs mcpo-github`

### Issue: "401 Unauthorized"
**Solution**: 
- Verify MCP_API_KEY matches in both .env and OpenWebUI
- Ensure Authorization header format: `Bearer YOUR_KEY`

### Issue: Tools not appearing in OpenWebUI
**Solution**:
- Wait 30 seconds after adding connection
- Refresh OpenWebUI page
- Check "Auto-append /openapi.json" is ON

## Summary of Working MCP Tools

| Port | Service | Description | Tools Count |
|------|---------|-------------|-------------|
| 8101 | OpenWebUI | AI Hub management | 165+ |
| 8102 | GitHub | Repository management | 15+ |
| 8103 | Filesystem | File operations | 10+ |
| 8104 | Brave Search | Web search | 5+ |
| 8105 | Memory | Knowledge storage | 8+ |

**Total Available Tools**: 200+ and growing!

## Next Steps
1. Deploy these services on your droplet
2. Add each to OpenWebUI
3. Test each tool category
4. Explore more MCP servers at: https://github.com/modelcontextprotocol/servers

Remember: Each tool category is isolated, so if one fails, others keep working!
