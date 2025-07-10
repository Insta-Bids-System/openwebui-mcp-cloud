#!/bin/bash

echo "🚀 Starting OpenWebUI with GitHub MCP Wrapper (Auto-Account Injection)"
echo "=================================================="

# Stop any existing services
echo "🛑 Stopping existing services..."
docker-compose -f docker-compose.simple-rollback.yml down --remove-orphans 2>/dev/null || true

# Start services with wrapper
echo "🏗️  Building and starting services with GitHub wrapper..."
docker-compose -f docker-compose.with-wrapper.yml up -d --build

# Wait for services to start
echo "⏳ Waiting for services to initialize..."
sleep 10

# Check service status
echo ""
echo "📊 Service Status:"
echo "=================="
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep -E "(local-|NAME)"

echo ""
echo "🔍 Health Checks:"
echo "=================="

# Check OpenWebUI
if curl -s http://localhost:8080/health > /dev/null 2>&1; then
    echo "✅ OpenWebUI (Port 8080): Healthy"
else
    echo "❌ OpenWebUI (Port 8080): Not responding"
fi

# Check OpenWebUI MCP (Port 8101)
if curl -s http://localhost:8101/health > /dev/null 2>&1; then
    echo "✅ OpenWebUI MCP (Port 8101): Healthy"
else
    echo "❌ OpenWebUI MCP (Port 8101): Not responding"
fi

# Check GitHub Wrapper (Port 8102)
if curl -s http://localhost:8102/health > /dev/null 2>&1; then
    echo "✅ GitHub MCP Wrapper (Port 8102): Healthy"
    
    # Show wrapper info
    echo ""
    echo "🔧 GitHub Wrapper Configuration:"
    echo "================================"
    curl -s http://localhost:8102/ | python3 -m json.tool 2>/dev/null || echo "Could not parse wrapper info"
else
    echo "❌ GitHub MCP Wrapper (Port 8102): Not responding"
fi

echo ""
echo "🎯 What's New with the Wrapper:"
echo "==============================="
echo "✅ Auto-injects 'Insta-Bids-System' for CREATE/UPDATE/DELETE operations"
echo "✅ Fixes the READ operations bug (no more 'your_username' errors)"
echo "✅ Preserves flexibility for READ operations (can access any public repo)"
echo "✅ No need to specify account name for your own repos - just say 'create a repo'"
echo "✅ All GitHub CRUD operations now work seamlessly"

echo ""
echo "💡 Test Commands:"
echo "================="
echo "CREATE/UPDATE/DELETE (auto-defaults to Insta-Bids-System):"
echo "• 'Create a repository called wrapper-test'"
echo "• 'Update the README in mcp-integration-test-2024'"
echo ""
echo "READ (flexible - can specify any account):"
echo "• 'List my repositories' (defaults to Insta-Bids-System)"
echo "• 'Get the README from facebook/react' (reads from facebook)"

echo ""
echo "🌐 Access Points:"
echo "================="
echo "• OpenWebUI: http://localhost:8080"
echo "• OpenWebUI MCP: http://localhost:8101"
echo "• GitHub Wrapper: http://localhost:8102"

echo ""
echo "📋 To stop services: docker-compose -f docker-compose.with-wrapper.yml down"
echo "" 