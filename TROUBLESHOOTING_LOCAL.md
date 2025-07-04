# 🔧 Local Testing Troubleshooting

## Services Won't Start

### Check Docker Desktop
```bash
# Is Docker running?
docker version

# If error, start Docker Desktop application
```

### Port Conflicts
```bash
# Check if ports are in use
netstat -an | findstr :8080
netstat -an | findstr :8101

# If in use, stop conflicting services or change ports in docker-compose.yml
```

### Container Errors
```bash
# Check logs
docker-compose logs open-webui-dev
docker-compose logs mcp-server-dev
docker-compose logs mcpo-openwebui-dev

# Restart everything
docker-compose down
docker-compose up -d
```

## MCP Tools Not Showing

### After Adding API Key
1. Must restart MCP services:
   ```bash
   docker-compose restart mcp-server-dev mcpo-openwebui-dev
   ```

2. In OpenWebUI Tools settings:
   - URL must be: `http://localhost:8101`
   - NOT `http://127.0.0.1:8101`
   - NOT `http://mcpo-openwebui:8101`

3. Test MCPO directly:
   ```bash
   curl http://localhost:8101/openapi.json
   ```
   Should return JSON with tool definitions

## Can't Access OpenWebUI

### Page Won't Load
1. Wait 1-2 minutes after `docker-compose up`
2. Check logs: `docker-compose logs open-webui-dev`
3. Try: http://127.0.0.1:8080 instead

### Blank Page
- Clear browser cache
- Try incognito/private window
- Check browser console for errors (F12)

## API Key Issues

### "Invalid API Key" Error
1. Make sure you copied the FULL key (including `sk-` prefix)
2. No extra spaces before/after key in `.env`
3. Restart services after adding key

### Forgot to Copy Key
- Go to Settings → Account → API Keys
- Delete old key
- Create new one
- Copy immediately!

## Model Issues

### No Models Available
- Must configure at least one provider
- See MODEL_SETUP.md for options

### Chat Errors
- Check your API key is valid
- Check you have credits/quota
- Try a different model

## Reset Everything

### Complete Fresh Start
```bash
# Stop and remove everything
docker-compose down -v

# Remove all data
docker system prune -a

# Start fresh
docker-compose up -d
```

## Still Stuck?

1. Check all logs:
   ```bash
   docker-compose logs > debug.log
   ```

2. Verify file exists:
   ```bash
   type .env
   ```

3. Check Docker resources:
   - Docker Desktop → Settings → Resources
   - Ensure 4GB+ RAM allocated