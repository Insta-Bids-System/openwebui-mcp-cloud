# 🔧 Troubleshooting Guide

Common issues and solutions for OpenWebUI MCP Cloud setup.

## 🚨 Quick Diagnostics

### Check Service Status
```bash
# Check all services
docker-compose -f docker-compose.enhanced.yml ps

# Check specific service
docker-compose -f docker-compose.enhanced.yml logs github-wrapper
docker-compose -f docker-compose.enhanced.yml logs filesystem-wrapper
```

### Test Service Endpoints
```bash
# Test all endpoints
services=("8102" "8107" "8104" "8105" "8106")
for port in "${services[@]}"; do
    curl -s http://localhost:$port/openapi.json > /dev/null && echo "Port $port: OK" || echo "Port $port: FAILED"
done
```

## 🔍 Common Issues

### 1. Services Won't Start

**Problem:** Docker containers not starting
```bash
# Check for errors
docker-compose -f docker-compose.enhanced.yml logs

# Common causes:
# - Port already in use
# - Missing .env file
# - Invalid environment variables
```

**Solutions:**
```bash
# Check port usage
lsof -i :8102
lsof -i :8107

# Kill conflicting processes
kill -9 $(lsof -t -i:8102)

# Restart Docker
sudo systemctl restart docker  # Linux
# or restart Docker Desktop

# Clean restart
docker-compose -f docker-compose.enhanced.yml down
docker-compose -f docker-compose.enhanced.yml up -d
```

### 2. GitHub Token Issues

**Problem:** GitHub operations failing
```
Error: "Bad credentials" or "API rate limit exceeded"
```

**Solutions:**
```bash
# Verify token in .env
cat .env | grep GITHUB_TOKEN

# Test token manually
curl -H "Authorization: Bearer $GITHUB_TOKEN" https://api.github.com/user

# Check token scopes (should include: repo, read:user, user:email)
# Regenerate token if needed: https://github.com/settings/tokens
```

### 3. Filesystem Path Issues

**Problem:** Files not found or wrong directory
```
Error: "No such file or directory"
```

**Solutions:**
```bash
# Check workspace directory exists
ls -la ./data/workspace/

# Create if missing
mkdir -p ./data/workspace

# Check wrapper path normalization logs
docker-compose -f docker-compose.enhanced.yml logs filesystem-wrapper | grep "Path normalized"

# Test path conversion manually
curl -X POST http://localhost:8107/list_directory \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer local-mcp-key-for-testing" \
  -d '{"path": "."}'
```

### 4. Tools Not Appearing in OpenWebUI

**Problem:** MCP tools not showing up in OpenWebUI Settings

**Solutions:**
```bash
# 1. Verify services are running
curl -s http://localhost:8102/openapi.json
curl -s http://localhost:8107/openapi.json

# 2. Check OpenWebUI can reach services
# In OpenWebUI settings, try adding:
# - http://localhost:8102 (GitHub Enhanced)
# - http://localhost:8107 (Filesystem Enhanced)

# 3. Restart OpenWebUI after adding tools
```

### 5. Wrong Tools Being Called

**Problem:** AI using wrong tools (e.g., `tool_list_workspace_files_post` instead of `tool_list_directory_post`)

**Solutions:**
```bash
# Check if using enhanced filesystem wrapper
# Should be: http://localhost:8107 (NOT 8104)

# Verify wrapper is redirecting tools
docker-compose -f docker-compose.enhanced.yml logs filesystem-wrapper | grep "Redirecting"

# Update OpenWebUI tools to use wrapper ports:
# - GitHub: http://localhost:8102 (wrapper)
# - Filesystem: http://localhost:8107 (wrapper)
```

### 6. Memory/Performance Issues

**Problem:** Slow responses or out of memory errors

**Solutions:**
```bash
# Check container resource usage
docker stats

# Increase memory limits in docker-compose.enhanced.yml
# Add under each service:
# deploy:
#   resources:
#     limits:
#       memory: 1G

# Restart with more resources
docker-compose -f docker-compose.enhanced.yml down
docker-compose -f docker-compose.enhanced.yml up -d
```

## 🔍 Debugging Steps

### 1. Enable Debug Logging
```bash
# Add to .env
DEBUG_LOGGING=true
LOG_LEVEL=DEBUG

# Restart services
./stop-enhanced.sh && ./start-enhanced.sh
```

### 2. Check Network Connectivity
```bash
# Test internal Docker network
docker network ls
docker network inspect openwebui-mcp-cloud_local-ai-net

# Test service-to-service communication
docker exec -it local-github-wrapper curl http://local-mcpo-github-internal:8000/openapi.json
```

### 3. Manual API Testing
```bash
# Test GitHub wrapper directly
curl -X POST http://localhost:8102/search_repositories \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer local-mcp-key-for-testing" \
  -d '{"query": "test"}'

# Test filesystem wrapper directly
curl -X POST http://localhost:8107/list_directory \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer local-mcp-key-for-testing" \
  -d '{"path": "/workspace"}'
```

## 📋 Environment-Specific Issues

### macOS Issues
```bash
# Port binding issues
sudo lsof -i :8102

# Permission issues with workspace
chmod -R 755 ./data/workspace/
```

### Linux Issues
```bash
# SELinux context issues
sudo setsebool -P container_use_cgroup_namespace on

# Firewall blocking ports
sudo ufw allow 8102
sudo ufw allow 8107
```

### Windows Issues
```bash
# Windows path issues
# Use forward slashes in docker-compose.yml volumes
# Example: ./data/workspace:/workspace (not .\data\workspace)

# Windows Defender blocking
# Add exclusion for project directory
```

## 🔄 Reset Procedures

### Soft Reset (Restart Services)
```bash
./stop-enhanced.sh
./start-enhanced.sh
```

### Hard Reset (Clean Everything)
```bash
# Stop and remove containers
docker-compose -f docker-compose.enhanced.yml down -v

# Remove images
docker rmi $(docker images 'openwebui-mcp-cloud*' -q)

# Clean workspace
rm -rf ./data/workspace/*

# Rebuild and restart
./start-enhanced.sh
```

### Nuclear Reset (Complete Clean)
```bash
# WARNING: This removes everything!
docker-compose -f docker-compose.enhanced.yml down -v
docker system prune -a --volumes
rm -rf ./data/
mkdir -p ./data/workspace
./start-enhanced.sh
```

## 📞 Getting Help

### Gather Information
Before asking for help, collect:
```bash
# System information
docker --version
docker-compose --version

# Service logs
docker-compose -f docker-compose.enhanced.yml logs > debug.log

# Environment configuration
cat .env | grep -v TOKEN | grep -v KEY  # Remove sensitive info
```

### Where to Get Help
- **GitHub Issues**: [Project Issues](https://github.com/yourusername/openwebui-mcp-cloud/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/openwebui-mcp-cloud/discussions)
- **OpenWebUI Community**: [OpenWebUI Discord](https://discord.gg/openwebui)

### Provide These Details
1. **Operating System**: (macOS, Linux, Windows)
2. **Docker Version**: `docker --version`
3. **Error Messages**: Copy exact error text
4. **Service Logs**: Relevant log excerpts
5. **Configuration**: Your `.env` file (remove sensitive tokens)
6. **Steps to Reproduce**: What you did before the error

---

## 🎯 Prevention Tips

1. **Always check logs first**: `docker-compose -f docker-compose.enhanced.yml logs`
2. **Use the wrapper ports**: 8102 (GitHub), 8107 (Filesystem)
3. **Keep API keys secure**: Never commit `.env` file
4. **Update regularly**: Pull latest changes and rebuild
5. **Monitor resources**: Use `docker stats` to watch usage
6. **Test after changes**: Run test scripts after configuration changes

**Remember: The enhanced wrappers solve most common issues automatically!** 🛡️ 