#!/bin/bash
# setup-droplet.sh - Initial setup script for DigitalOcean Droplet

set -e

echo "🚀 Starting OpenWebUI + MCP Cloud Setup..."

# Update system
echo "📦 Updating system packages..."
apt-get update && apt-get upgrade -y

# Install Docker if not already installed
if ! command -v docker &> /dev/null; then
    echo "🐳 Installing Docker..."
    curl -fsSL https://get.docker.com | sh
fi

# Install Docker Compose
echo "🐳 Installing Docker Compose..."
apt-get install -y docker-compose

# Install additional tools
echo "🔧 Installing additional tools..."
apt-get install -y nginx certbot python3-certbot-nginx ufw fail2ban git

# Create directory structure
echo "📁 Creating directory structure..."
mkdir -p /data/{workspace,openwebui/backend,nginx/ssl,filebrowser,redis,backups,mcp-configs}
chmod -R 755 /data

# Configure firewall
echo "🔒 Configuring firewall..."
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 8101:8105/tcp  # MCP ports
ufw --force enable

# Setup fail2ban for security
echo "🛡️ Setting up fail2ban..."
systemctl enable fail2ban
systemctl start fail2ban
# Clone repository
echo "📥 Cloning repository..."
cd /root
if [ -d "openwebui-mcp-cloud" ]; then
    echo "Repository already exists, pulling latest changes..."
    cd openwebui-mcp-cloud
    git pull
else
    git clone https://github.com/YOUR-USERNAME/openwebui-mcp-cloud.git
    cd openwebui-mcp-cloud
fi

# Create environment file
echo "🔐 Creating environment file..."
if [ ! -f ".env.production" ]; then
    cp .env.template .env.production
    echo "⚠️  Please edit .env.production with your actual values!"
fi

# Generate secure passwords
echo "🔑 Generating secure passwords..."
echo "WEBUI_SECRET_KEY=$(openssl rand -hex 32)" >> .env.production
echo "MCP_API_KEY=$(openssl rand -hex 32)" >> .env.production
echo "FB_PASSWORD=$(openssl rand -base64 16)" >> .env.production

# Create nginx password file
echo "🔐 Creating nginx password file..."
FB_USERNAME=admin
FB_PASSWORD=$(openssl rand -base64 16)
htpasswd -cb /etc/nginx/.htpasswd $FB_USERNAME $FB_PASSWORD

echo "✅ Setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Edit /root/openwebui-mcp-cloud/.env.production with your database URLs"
echo "2. Run: docker-compose -f docker-compose.production.yml up -d"
echo "3. Access OpenWebUI and generate API key"
echo "4. Update OPENWEBUI_API_KEY in .env.production"
echo "5. Restart MCP server: docker-compose -f docker-compose.production.yml restart mcp-server"
echo ""
echo "FileBrowser credentials:"
echo "Username: $FB_USERNAME"
echo "Password: $FB_PASSWORD"