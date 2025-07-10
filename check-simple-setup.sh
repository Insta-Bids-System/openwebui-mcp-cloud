#!/bin/bash

echo "🔍 Checking Simple OpenWebUI MCP Setup (Ports 8101 & 8102)"
echo "============================================================"

# Check if docker-compose services are running
echo "📦 Docker Services:"
docker-compose -f docker-compose.simple-rollback.yml ps

echo ""
echo "🔌 Testing MCP Endpoints:"

# Test Port 8101 (OpenWebUI Control)
echo -n "   Port 8101 (OpenWebUI Control): "
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" -H "Authorization: Bearer local-mcp-key-for-testing" http://localhost:8101/docs)
if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ Working"
else
    echo "❌ Failed (HTTP $HTTP_CODE)"
fi

# Test Port 8102 (GitHub Tools)
echo -n "   Port 8102 (GitHub Tools): "
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" -H "Authorization: Bearer local-mcp-key-for-testing" http://localhost:8102/docs)
if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ Working"
else
    echo "❌ Failed (HTTP $HTTP_CODE)"
fi

# Test OpenWebUI
echo -n "   Port 8080 (OpenWebUI): "
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/)
if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ Working"
else
    echo "❌ Failed (HTTP $HTTP_CODE)"
fi

echo ""
echo "🧪 Testing Tools:"

# Test OpenWebUI Control health
echo -n "   OpenWebUI Health Check: "
RESPONSE=$(curl -s -X POST "http://localhost:8101/get_health" -H "Authorization: Bearer local-mcp-key-for-testing" -H "Content-Type: application/json" -d "{}")
if echo "$RESPONSE" | grep -q '"status":true'; then
    echo "✅ Healthy"
else
    echo "❌ Failed"
fi

# Test GitHub search (simplified)
echo -n "   GitHub Search Test: "
RESPONSE=$(curl -s -X POST "http://localhost:8102/search_repositories" -H "Authorization: Bearer local-mcp-key-for-testing" -H "Content-Type: application/json" -d '{"query": "test", "limit": 1}')
if echo "$RESPONSE" | grep -q '"total_count"'; then
    echo "✅ Working"
else
    echo "❌ Failed"
fi

echo ""
echo "🎯 Summary:"
echo "   - Port 8101: OpenWebUI Administrative tools (users, models, chats, workspace files)"
echo "   - Port 8102: GitHub tools (repositories, issues, PRs, search)"
echo "   - Port 8080: OpenWebUI interface"
echo ""
echo "💡 Access URLs:"
echo "   - OpenWebUI: http://localhost:8080"
echo "   - Port 8101 API Docs: http://localhost:8101/docs (auth: Bearer local-mcp-key-for-testing)"
echo "   - Port 8102 API Docs: http://localhost:8102/docs (auth: Bearer local-mcp-key-for-testing)" 