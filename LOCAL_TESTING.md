# 🧪 Local Testing Guide

## Quick Start for Local Testing

### 1. Navigate to Project Directory
```bash
cd C:\Users\USER\Documents\openwebui-mcp-cloud
```

### 2. Copy Local Environment File
```bash
copy .env.local .env
```

### 3. Start Services (Development Mode)
```bash
docker-compose up -d
```

This will start:
- OpenWebUI on http://localhost:8080
- MCPO-OpenWebUI on http://localhost:8101

### 4. Initialize OpenWebUI
1. Open browser: http://localhost:8080
2. Create admin account (first user becomes admin)
3. Go to Settings → Account → API Keys
4. Generate API key and copy it

### 5. Update MCP Configuration
1. Edit `.env` file
2. Add: `OPENWEBUI_API_KEY=your-copied-key`
3. Restart MCP server:
   ```bash
   docker-compose restart mcp-server mcpo-openwebui
   ```

### 6. Configure MCP Tools in OpenWebUI
1. Go to Settings → Tools
2. Add tool URL: `http://localhost:8101`
3. Enable "Auto-append /openapi.json"
4. Save changes

### 7. Test MCP Tools
In chat, try:
- "Show me available tools"
- "List all users"
- "Check system health"

## Troubleshooting Local Setup

### If containers won't start:
```bash
# Check logs
docker-compose logs -f

# Check port conflicts
netstat -an | findstr :8080
netstat -an | findstr :8101
```

### If MCP tools don't appear:
1. Verify MCPO is running: `docker ps`
2. Test endpoint: `curl http://localhost:8101/openapi.json`
3. Check OpenWebUI tool configuration

### To stop everything:
```bash
docker-compose down
```

### To clean up completely:
```bash
docker-compose down -v
docker system prune -a
```