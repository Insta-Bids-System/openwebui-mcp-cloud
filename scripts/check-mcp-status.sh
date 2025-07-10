#!/bin/bash
# check-mcp-status.sh - Check status of all MCP tools

echo "🔍 MCP Tools Status Check"
echo "========================"

# Function to check service
check_service() {
    local name=$1
    local port=$2
    local container="mcpo-$name"
    
    echo -n "[$name] Port $port: "
    
    # Check if container is running
    if docker ps | grep -q "$container"; then
        # Check if endpoint responds
        if curl -s -f "http://localhost:$port/openapi.json" > /dev/null 2>&1; then
            count=$(curl -s "http://localhost:$port/openapi.json" | grep -o '"operationId"' | wc -l)
            echo "✅ Running ($count tools available)"
        else
            echo "⚠️  Container running but API not responding"
            echo "   Check logs: docker logs $container"
        fi
    else
        echo "❌ Container not running"
        echo "   Start with: docker-compose up -d $container"
    fi
}

echo ""
check_service "openwebui" 8101
check_service "github" 8102
check_service "filesystem" 8103
check_service "brave-search" 8104
check_service "memory" 8105

echo ""
echo "📊 Summary:"
docker ps | grep mcpo | wc -l | xargs echo "Active MCPO containers:"

echo ""
echo "💡 To view logs for any service:"
echo "   docker logs -f mcpo-[service-name]"
echo ""
echo "🔧 To restart all services:"
echo "   docker-compose -f docker-compose.production.yml restart"
