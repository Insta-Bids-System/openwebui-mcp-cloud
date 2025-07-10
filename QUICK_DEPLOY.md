# 🚀 Quick Droplet Deployment Guide

## Prerequisites
- DigitalOcean account
- Domain pointing to Droplet
- PostgreSQL database (Supabase/DigitalOcean Managed)
- Redis instance (DigitalOcean Managed)

## Step 1: Create Droplet
1. Go to DigitalOcean Console
2. Create Droplet with:
   - **Image**: Ubuntu 22.04 LTS
   - **Size**: Basic → Regular → $48/month (4 vCPU, 8GB RAM)
   - **Region**: Choose closest
   - **Authentication**: SSH Key (recommended)
   - **Hostname**: openwebui-mcp-droplet

## Step 2: Initial Setup
```bash
# SSH into your droplet
ssh root@YOUR_DROPLET_IP

# Download and run setup script
wget https://raw.githubusercontent.com/YOUR-USERNAME/openwebui-mcp-cloud/main/scripts/setup-droplet.sh
chmod +x setup-droplet.sh
./setup-droplet.sh
```

## Step 3: Configure Environment
```bash
cd /root/openwebui-mcp-cloud
nano .env.production
```

Add your actual values:
- PostgreSQL URL from Supabase/DO
- Redis URL from DO Managed Redis
- Your domain name

## Step 4: Deploy Services
```bash
docker-compose -f docker-compose.production.yml up -d
```
## Step 5: Initialize OpenWebUI
1. Access: http://YOUR_DROPLET_IP
2. Create admin account
3. Go to Settings → Account → API Keys
4. Generate new API key
5. Copy the key

## Step 6: Update MCP Configuration
```bash
# Add API key to environment
nano .env.production
# Add: OPENWEBUI_API_KEY=your-generated-key

# Restart MCP server
docker-compose -f docker-compose.production.yml restart mcp-server
```

## Step 7: Setup SSL
```bash
# Point domain to Droplet IP first!
certbot --nginx -d your-domain.com
```

## Step 8: Configure OpenWebUI Tools
1. Go to OpenWebUI Settings → Tools
2. Add tool URL: `http://YOUR_DROPLET_IP:8101`
3. Enable "Auto-append /openapi.json"
4. Save and test

## Step 9: Test Everything
- **OpenWebUI**: https://your-domain.com
- **FileBrowser**: https://your-domain.com/files
- **MCP Tools**: Test in chat with "list available tools"

## 🎉 Success Indicators
- All containers show as "Up" in `docker ps`
- Can access all web interfaces
- MCP tools show in OpenWebUI
- Files persist in /data/workspace

## 🚨 Common Issues
- **Tools not showing**: Use public IP, not localhost
- **Redis errors**: Add `?ssl_cert_reqs=none&decode_responses=true`
- **Lost data**: Always use external databases

## 📧 Support
For issues, check logs:
```bash
docker-compose -f docker-compose.production.yml logs -f
```