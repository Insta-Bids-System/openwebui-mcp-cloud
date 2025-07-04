#!/bin/bash
# health-check.sh - System health monitoring script

echo "🏥 System Health Check"
echo "====================="
echo ""

# Check Docker services
echo "🐳 Docker Services:"
docker-compose -f /root/openwebui-mcp-cloud/docker-compose.production.yml ps

echo ""
echo "📊 Resource Usage:"
docker stats --no-stream

echo ""
echo "🔍 Service Health Checks:"

# Check OpenWebUI
echo -n "OpenWebUI: "
if curl -f http://localhost:8080/health > /dev/null 2>&1; then
    echo "✅ Healthy"
else
    echo "❌ Unhealthy"
fi

# Check MCPO services
for port in 8101 8102 8103; do
    echo -n "MCPO on port $port: "
    if curl -f http://localhost:$port/openapi.json > /dev/null 2>&1; then
        echo "✅ Healthy"
    else
        echo "❌ Unhealthy"
    fi
done

# Check disk space
echo ""
echo "💾 Disk Usage:"
df -h | grep -E '^/dev/'

# Check memory
echo ""
echo "🧠 Memory Usage:"
free -h

# Check recent errors
echo ""
echo "⚠️  Recent Errors (last 20 lines):"
docker-compose -f /root/openwebui-mcp-cloud/docker-compose.production.yml logs --tail=20 2>&1 | grep -i error || echo "No recent errors found"