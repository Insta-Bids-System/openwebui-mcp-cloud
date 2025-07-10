#!/bin/bash
# deploy-mcp-tools.sh - Quick deployment script for adding MCP tools

echo "🚀 Deploying Additional MCP Tools..."

# Check if we're on the DigitalOcean droplet
if [ ! -f "/root/ai-hub-cloud/docker-compose.production.yml" ]; then
    echo "❌ Error: This script must be run on your DigitalOcean droplet"
    echo "SSH into your droplet first: ssh root@159.65.36.162"
    exit 1
fi

cd /root/ai-hub-cloud

# Backup current config
cp docker-compose.production.yml docker-compose.production.yml.backup
echo "✅ Backed up current configuration"

# Pull latest MCPO image
echo "📦 Pulling latest MCPO image..."
docker pull ghcr.io/open-webui/mcpo:main

# Create required directories
mkdir -p /data/memory
echo "✅ Created required directories"

# Check environment variables
echo "🔍 Checking required environment variables..."
if ! grep -q "GITHUB_TOKEN" .env.production; then
    echo "⚠️  Missing GITHUB_TOKEN in .env.production"
    echo "   Add: GITHUB_TOKEN=ghp_your_token_here"
fi

if ! grep -q "BRAVE_API_KEY" .env.production; then
    echo "⚠️  Missing BRAVE_API_KEY in .env.production"
    echo "   Add: BRAVE_API_KEY=your_api_key_here"
fi

# Restart services
echo "🔄 Restarting services..."
docker-compose -f docker-compose.production.yml up -d

# Wait for services to start
sleep 10

# Check service status
echo "📊 Checking service status..."
docker-compose -f docker-compose.production.yml ps

# Test each endpoint
echo "🧪 Testing MCP endpoints..."

test_endpoint() {
    local port=$1
    local name=$2
    echo -n "Testing $name (port $port)... "
    
    if curl -s -f "http://localhost:$port/openapi.json" > /dev/null 2>&1; then
        echo "✅ Working"
    else
        echo "❌ Failed - Check logs with: docker logs mcpo-$name"
    fi
}

test_endpoint 8101 "openwebui"
test_endpoint 8102 "github"
test_endpoint 8103 "filesystem"
test_endpoint 8104 "brave-search"
test_endpoint 8105 "memory"

echo ""
echo "✅ Deployment complete!"
echo ""
echo "📝 Next steps:"
echo "1. Add any missing API keys to .env.production"
echo "2. Go to OpenWebUI Admin Panel → Tools → Add Connection"
echo "3. Add each service using http://159.65.36.162:PORT"
echo "4. Use the same MCP_API_KEY for all services"
echo ""
echo "📚 Available endpoints:"
echo "   - GitHub:     http://159.65.36.162:8102"
echo "   - Filesystem: http://159.65.36.162:8103" 
echo "   - Search:     http://159.65.36.162:8104"
echo "   - Memory:     http://159.65.36.162:8105"
