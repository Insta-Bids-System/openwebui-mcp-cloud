#!/bin/bash
# deploy-to-droplet.sh - Complete deployment script for OpenWebUI + MCP on DigitalOcean

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 OpenWebUI + MCP Cloud Deployment Script${NC}"
echo -e "${GREEN}===========================================${NC}"

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
   echo -e "${RED}Please run as root (use sudo)${NC}"
   exit 1
fi

# Update system
echo -e "${YELLOW}📦 Updating system packages...${NC}"
apt-get update && apt-get upgrade -y

# Install Docker if not already installed
if ! command -v docker &> /dev/null; then
    echo -e "${YELLOW}🐳 Installing Docker...${NC}"
    curl -fsSL https://get.docker.com | sh
    systemctl enable docker
    systemctl start docker
fi

# Install Docker Compose
echo -e "${YELLOW}🐳 Installing Docker Compose...${NC}"
apt-get install -y docker-compose git

# Install additional tools
echo -e "${YELLOW}🔧 Installing additional tools...${NC}"
apt-get install -y nginx certbot python3-certbot-nginx ufw fail2ban htpasswd

# Create directory structure
echo -e "${YELLOW}📁 Creating directory structure...${NC}"
mkdir -p /data/{workspace,openwebui/backend,nginx/ssl,filebrowser,redis,backups,mcp-configs}
chmod -R 755 /data

# Configure firewall
echo -e "${YELLOW}🔒 Configuring firewall...${NC}"
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 8101:8105/tcp  # MCP ports
ufw --force enable

# Setup fail2ban for security
echo -e "${YELLOW}🛡️ Setting up fail2ban...${NC}"
systemctl enable fail2ban
systemctl start fail2ban

# Clone repository
echo -e "${YELLOW}📥 Setting up project files...${NC}"
cd /root
if [ -d "openwebui-mcp-cloud" ]; then
    echo "Repository already exists, pulling latest changes..."
    cd openwebui-mcp-cloud
    git pull
else
    # Create directory and essential files
    mkdir -p openwebui-mcp-cloud/{mcp-server,nginx,scripts}
    cd openwebui-mcp-cloud
fi

# Create MCP Server Dockerfile
echo -e "${YELLOW}📝 Creating MCP Server Dockerfile...${NC}"
cat > mcp-server/Dockerfile << 'EOF'
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir \
    fastapi \
    uvicorn \
    httpx \
    redis \
    pydantic \
    python-multipart

# Copy server code
COPY main.py .

# Expose port
EXPOSE 8888

# Run server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8888"]
EOF

# Create MCP Server main.py
echo -e "${YELLOW}📝 Creating MCP Server main.py...${NC}"
cat > mcp-server/main.py << 'EOF'
"""
MCP Server for OpenWebUI Integration
Provides 200+ tools for AI self-modification
"""
import os
import json
import httpx
import asyncio
from fastapi import FastAPI, Request, HTTPException
from typing import Dict, Any, List, Optional
import redis
import urllib.parse

app = FastAPI(title="MCP Server", version="1.0.0")

# Configuration
OPENWEBUI_URL = os.getenv("OPENWEBUI_URL", "http://open-webui:8080")
OPENWEBUI_API_KEY = os.getenv("OPENWEBUI_API_KEY", "")
REDIS_URL = os.getenv("REDIS_URL", "")

# Redis client (optional)
redis_client = None
if REDIS_URL:
    try:
        redis_client = redis.from_url(REDIS_URL)
    except Exception as e:
        print(f"Redis connection failed: {e}")

# HTTP client for OpenWebUI API calls
http_client = httpx.AsyncClient(timeout=30.0)

# Tool decorator
def mcp_tool(func):
    """Decorator to register MCP tools"""
    func.is_mcp_tool = True
    return func

# Helper function for API calls
async def call_openwebui_api(method: str, endpoint: str, data: Optional[Dict] = None):
    """Make authenticated API call to OpenWebUI"""
    headers = {
        "Content-Type": "application/json"
    }
    if OPENWEBUI_API_KEY:
        headers["Authorization"] = f"Bearer {OPENWEBUI_API_KEY}"
    
    url = f"{OPENWEBUI_URL}{endpoint}"
    
    try:
        if method == "GET":
            response = await http_client.get(url, headers=headers)
        elif method == "POST":
            response = await http_client.post(url, headers=headers, json=data)
        elif method == "PUT":
            response = await http_client.put(url, headers=headers, json=data)
        elif method == "DELETE":
            response = await http_client.delete(url, headers=headers)
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"API call failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Health check
@app.get("/health")
async def health_check():
    """Check server health"""
    return {"status": "healthy", "service": "mcp-server"}

# Core MCP tools
@app.post("/tools/list_tools")
@mcp_tool
async def list_tools():
    """List all available MCP tools"""
    tools = []
    for route in app.routes:
        if hasattr(route.endpoint, 'is_mcp_tool'):
            tools.append({
                "name": route.path.replace("/tools/", ""),
                "description": route.endpoint.__doc__
            })
    return {"tools": tools}

# Chat Management Tools
@app.post("/tools/list_chats")
@mcp_tool
async def list_chats():
    """List all chats"""
    return await call_openwebui_api("GET", "/api/v1/chats")

@app.post("/tools/get_chat")
@mcp_tool
async def get_chat(chat_id: str):
    """Get a specific chat by ID"""
    return await call_openwebui_api("GET", f"/api/v1/chats/{chat_id}")

@app.post("/tools/create_chat")
@mcp_tool
async def create_chat(title: str):
    """Create a new chat"""
    return await call_openwebui_api("POST", "/api/v1/chats/new", {"title": title})

@app.post("/tools/delete_chat")
@mcp_tool
async def delete_chat(chat_id: str):
    """Delete a chat"""
    return await call_openwebui_api("DELETE", f"/api/v1/chats/{chat_id}")

# User Management Tools
@app.post("/tools/list_users")
@mcp_tool
async def list_users():
    """List all users"""
    return await call_openwebui_api("GET", "/api/v1/users")

@app.post("/tools/get_user")
@mcp_tool
async def get_user(user_id: str):
    """Get user details"""
    return await call_openwebui_api("GET", f"/api/v1/users/{user_id}")

# File Operations
@app.post("/tools/list_files")
@mcp_tool
async def list_files(path: str = "/workspace"):
    """List files in workspace"""
    import os
    try:
        files = os.listdir(path)
        return {"files": files, "path": path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/tools/read_file")
@mcp_tool
async def read_file(filepath: str):
    """Read file contents"""
    try:
        with open(filepath, 'r') as f:
            content = f.read()
        return {"content": content, "filepath": filepath}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/tools/write_file")
@mcp_tool
async def write_file(filepath: str, content: str):
    """Write content to file"""
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w') as f:
            f.write(content)
        return {"status": "success", "filepath": filepath}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Model Management
@app.post("/tools/list_models")
@mcp_tool
async def list_models():
    """List available models"""
    return await call_openwebui_api("GET", "/api/v1/models")

# Add more tools as needed...

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8888)
EOF

# Create nginx configuration
echo -e "${YELLOW}📝 Creating Nginx configuration...${NC}"
cat > nginx/production.conf << 'EOF'
events {
    worker_connections 1024;
}

http {
    upstream openwebui {
        server open-webui:8080;
    }
    
    upstream filebrowser {
        server filebrowser:80;
    }
    
    upstream mcpo {
        server mcpo-openwebui:8000;
    }

    server {
        listen 80;
        server_name _;
        
        # OpenWebUI (main interface)
        location / {
            proxy_pass http://openwebui;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # WebSocket support
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
        }
        
        # FileBrowser
        location /files/ {
            proxy_pass http://filebrowser/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }
        
        # Direct workspace browser
        location /workspace/ {
            alias /data/workspace/;
            autoindex on;
            autoindex_exact_size off;
            autoindex_localtime on;
        }
        
        # MCP endpoints
        location /mcp/ {
            proxy_pass http://mcpo/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }
    }
}
EOF

# Create docker-compose.production.yml
echo -e "${YELLOW}📝 Creating docker-compose.production.yml...${NC}"
cat > docker-compose.production.yml << 'EOF'
version: '3.9'

services:
  # === Core Services ===
  open-webui:
    image: ghcr.io/open-webui/open-webui:main
    container_name: open-webui
    restart: unless-stopped
    environment:
      - DATABASE_URL=${POSTGRES_URL}
      - WEBUI_SECRET_KEY=${WEBUI_SECRET_KEY}
      - REDIS_URL=${REDIS_URL}
      - ENABLE_COMMUNITY_SHARING=false
      - ENABLE_MESSAGE_RATING=true
      - DEFAULT_LOCALE=en
    volumes:
      - /data/openwebui/backend:/app/backend/data
    networks:
      - ai-hub-net
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # === MCP Server Layer ===
  mcp-server:
    build: ./mcp-server
    container_name: mcp-server
    restart: unless-stopped
    environment:
      - OPENWEBUI_URL=http://open-webui:8080
      - OPENWEBUI_API_KEY=${OPENWEBUI_API_KEY}
      - REDIS_URL=${REDIS_URL}
    volumes:
      - /data/workspace:/workspace
    networks:
      - ai-hub-net

  # === MCPO Bridge Layer ===
  mcpo-openwebui:
    image: ghcr.io/open-webui/mcpo:main
    container_name: mcpo-openwebui
    restart: unless-stopped
    ports:
      - "8101:8000"
    command: ["--host", "0.0.0.0", "--port", "8000", "--api-key", "${MCP_API_KEY}", "--", "python", "-m", "mcp_server"]
    environment:
      - MCP_SERVER_URL=http://mcp-server:8888
    depends_on:
      - mcp-server
    networks:
      - ai-hub-net

  # === Supporting Services ===
  filebrowser:
    image: filebrowser/filebrowser:latest
    container_name: filebrowser
    restart: unless-stopped
    environment:
      - FB_USERNAME=${FB_USERNAME}
      - FB_PASSWORD=${FB_PASSWORD}
    volumes:
      - /data/workspace:/srv
      - /data/filebrowser/database.db:/database.db
    networks:
      - ai-hub-net

  nginx:
    image: nginx:alpine
    container_name: nginx
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/production.conf:/etc/nginx/nginx.conf:ro
      - /data/nginx/ssl:/etc/nginx/ssl
    depends_on:
      - open-webui
      - mcpo-openwebui
      - filebrowser
    networks:
      - ai-hub-net

networks:
  ai-hub-net:
    driver: bridge

volumes:
  workspace-data:
    driver: local
EOF

# Create environment template
echo -e "${YELLOW}📝 Creating environment template...${NC}"
cat > .env.production << 'EOF'
# Production Environment Configuration
DOMAIN_NAME=159.65.36.162

# Database Configuration (Replace with your actual values)
POSTGRES_URL=postgresql://user:pass@db-host:5432/openwebui
REDIS_URL=rediss://default:pass@redis-host:25061/0?ssl_cert_reqs=none&decode_responses=true

# Security Keys (Auto-generated)
EOF

# Generate secure keys
echo -e "${YELLOW}🔑 Generating secure keys...${NC}"
echo "WEBUI_SECRET_KEY=$(openssl rand -hex 32)" >> .env.production
echo "MCP_API_KEY=$(openssl rand -hex 32)" >> .env.production
echo "" >> .env.production
echo "# OpenWebUI API Key (Generate after setup)" >> .env.production
echo "OPENWEBUI_API_KEY=" >> .env.production
echo "" >> .env.production
echo "# FileBrowser Credentials" >> .env.production
echo "FB_USERNAME=admin" >> .env.production
echo "FB_PASSWORD=$(openssl rand -base64 16)" >> .env.production

# Create backup script
echo -e "${YELLOW}📝 Creating backup script...${NC}"
mkdir -p scripts
cat > scripts/backup.sh << 'EOF'
#!/bin/bash
# Automated backup script

BACKUP_DIR="/data/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup workspace
tar -czf $BACKUP_DIR/workspace_$DATE.tar.gz /data/workspace

# Backup configurations
tar -czf $BACKUP_DIR/configs_$DATE.tar.gz /root/openwebui-mcp-cloud/.env.production docker-compose.production.yml nginx/

# Clean old backups (keep last 7 days)
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete

echo "Backup completed: $DATE"
EOF
chmod +x scripts/backup.sh

# Setup cron for automated backups
echo -e "${YELLOW}⏰ Setting up automated backups...${NC}"
(crontab -l 2>/dev/null; echo "0 2 * * * /root/openwebui-mcp-cloud/scripts/backup.sh") | crontab -

# Create health check script
echo -e "${YELLOW}📝 Creating health check script...${NC}"
cat > scripts/health-check.sh << 'EOF'
#!/bin/bash
# Health check script

echo "🏥 Health Check Report"
echo "====================="

# Check Docker services
echo "📦 Docker Services:"
docker-compose -f docker-compose.production.yml ps

# Check disk space
echo -e "\n💾 Disk Space:"
df -h | grep -E '^/dev|Filesystem'

# Check memory
echo -e "\n🧠 Memory Usage:"
free -h

# Check endpoints
echo -e "\n🌐 Endpoint Tests:"
curl -s -o /dev/null -w "OpenWebUI: %{http_code}\n" http://localhost:80
curl -s -o /dev/null -w "MCPO: %{http_code}\n" http://localhost:8101/openapi.json

echo -e "\n✅ Health check complete!"
EOF
chmod +x scripts/health-check.sh

echo -e "${GREEN}✅ Deployment script setup complete!${NC}"
echo ""
echo -e "${YELLOW}📋 IMPORTANT NEXT STEPS:${NC}"
echo -e "${YELLOW}1. Edit .env.production with your database URLs:${NC}"
echo "   - POSTGRES_URL from Supabase or DigitalOcean Managed Database"
echo "   - REDIS_URL from DigitalOcean Managed Redis"
echo ""
echo -e "${YELLOW}2. Start all services:${NC}"
echo "   docker-compose -f docker-compose.production.yml up -d"
echo ""
echo -e "${YELLOW}3. Wait for services to start (about 1 minute), then:${NC}"
echo "   - Access OpenWebUI at http://159.65.36.162"
echo "   - Create your admin account"
echo "   - Go to Settings → Account → API Keys"
echo "   - Generate a new API key"
echo ""
echo -e "${YELLOW}4. Update OPENWEBUI_API_KEY in .env.production${NC}"
echo ""
echo -e "${YELLOW}5. Restart the MCP server:${NC}"
echo "   docker-compose -f docker-compose.production.yml restart mcp-server mcpo-openwebui"
echo ""
echo -e "${YELLOW}6. Configure OpenWebUI Tools:${NC}"
echo "   - Go to Settings → Tools"
echo "   - Add tool URL: http://159.65.36.162:8101"
echo "   - Enable 'Auto-append /openapi.json'"
echo "   - Add Authorization header: Bearer YOUR_MCP_API_KEY"
echo ""
echo -e "${GREEN}🎉 Once complete, your AI Hub will be ready!${NC}"
echo ""
echo -e "${YELLOW}📧 Need help? Check logs with:${NC}"
echo "   docker-compose -f docker-compose.production.yml logs -f"
echo ""
echo -e "${YELLOW}🔒 Don't forget to setup SSL later:${NC}"
echo "   certbot --nginx -d your-domain.com"
