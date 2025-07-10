#!/bin/bash

# Health Check Script for OpenWebUI MCP Cloud
# Tests all services and reports status

set -e

echo "🏥 OpenWebUI MCP Cloud Health Check"
echo "=================================="

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Track overall health
OVERALL_HEALTH=0

# Function to check service endpoint
check_service() {
    local name=$1
    local port=$2
    local endpoint=$3
    
    echo -n "Checking $name (port $port)... "
    
    if curl -s -f "http://localhost:$port$endpoint" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ OK${NC}"
        return 0
    else
        echo -e "${RED}❌ FAILED${NC}"
        OVERALL_HEALTH=1
        return 1
    fi
}

# Function to check container status
check_container() {
    local name=$1
    echo -n "Checking container $name... "
    
    if docker ps --format "table {{.Names}}" | grep -q "^$name$"; then
        echo -e "${GREEN}✅ Running${NC}"
        return 0
    else
        echo -e "${RED}❌ Not Running${NC}"
        OVERALL_HEALTH=1
        return 1
    fi
}

# Function to test API functionality
test_api() {
    local name=$1
    local port=$2
    local test_data=$3
    local endpoint=$4
    
    echo -n "Testing $name API... "
    
    response=$(curl -s -X POST "http://localhost:$port$endpoint" \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer local-mcp-key-for-testing" \
        -d "$test_data" 2>/dev/null)
    
    if [ $? -eq 0 ] && [ ! -z "$response" ]; then
        echo -e "${GREEN}✅ OK${NC}"
        return 0
    else
        echo -e "${RED}❌ FAILED${NC}"
        OVERALL_HEALTH=1
        return 1
    fi
}

echo ""
echo "📦 Container Status:"
echo "-------------------"
check_container "local-github-wrapper"
check_container "local-filesystem-wrapper"
check_container "local-mcpo-github-internal"
check_container "local-mcpo-filesystem"
check_container "local-mcpo-brave-search"
check_container "local-mcpo-memory"

echo ""
echo "🌐 Service Endpoints:"
echo "-------------------"
check_service "GitHub Wrapper" "8102" "/openapi.json"
check_service "Filesystem Wrapper" "8107" "/openapi.json"
check_service "Filesystem MCP" "8104" "/openapi.json"
check_service "Search MCP" "8105" "/openapi.json"
check_service "Memory MCP" "8106" "/openapi.json"

echo ""
echo "🧪 API Functionality:"
echo "-------------------"

# Test filesystem wrapper path normalization
test_api "Filesystem Path Normalization" "8107" '{"path": "."}' "/list_directory"

# Test GitHub wrapper (if token is configured)
if [ -f ".env" ] && grep -q "GITHUB_TOKEN.*=" .env && ! grep -q "GITHUB_TOKEN=your_github_token_here" .env; then
    test_api "GitHub API" "8102" '{"query": "test"}' "/search_repositories"
else
    echo -e "GitHub API... ${YELLOW}⚠️ SKIPPED (Token not configured)${NC}"
fi

# Test search (if key is configured)
if [ -f ".env" ] && grep -q "BRAVE_SEARCH_API_KEY.*=" .env && ! grep -q "BRAVE_SEARCH_API_KEY=your_brave_search_key_here" .env; then
    test_api "Search API" "8105" '{"query": "test"}' "/search"
else
    echo -e "Search API... ${YELLOW}⚠️ SKIPPED (API key not configured)${NC}"
fi

echo ""
echo "📁 Workspace Check:"
echo "-----------------"
echo -n "Checking workspace directory... "
if [ -d "./data/workspace" ]; then
    echo -e "${GREEN}✅ OK${NC}"
    echo "   Path: $(realpath ./data/workspace)"
    echo "   Files: $(ls -la ./data/workspace | wc -l) items"
else
    echo -e "${RED}❌ Missing${NC}"
    echo "   Creating workspace directory..."
    mkdir -p ./data/workspace
    echo -e "   ${GREEN}✅ Created${NC}"
fi

echo ""
echo "🔧 Configuration Check:"
echo "----------------------"
echo -n "Checking .env file... "
if [ -f ".env" ]; then
    echo -e "${GREEN}✅ OK${NC}"
    
    # Check required variables
    if grep -q "GITHUB_TOKEN=your_github_token_here" .env; then
        echo -e "   ${YELLOW}⚠️ GitHub token not configured${NC}"
    else
        echo -e "   ${GREEN}✅ GitHub token configured${NC}"
    fi
    
    if grep -q "BRAVE_SEARCH_API_KEY=" .env; then
        echo -e "   ${GREEN}✅ Search API key configured${NC}"
    else
        echo -e "   ${YELLOW}⚠️ Search API key not configured${NC}"
    fi
else
    echo -e "${RED}❌ Missing${NC}"
    echo "   Run: cp .env.minimal .env"
    OVERALL_HEALTH=1
fi

echo ""
echo "🔗 Network Check:"
echo "---------------"
echo -n "Checking Docker network... "
if docker network ls | grep -q "local-ai-net"; then
    echo -e "${GREEN}✅ OK${NC}"
else
    echo -e "${RED}❌ Missing${NC}"
    OVERALL_HEALTH=1
fi

echo ""
echo "💾 Resource Usage:"
echo "----------------"
echo "Container resource usage:"
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}" | grep -E "(local-|CONTAINER)"

echo ""
echo "🎯 Summary:"
echo "----------"
if [ $OVERALL_HEALTH -eq 0 ]; then
    echo -e "${GREEN}🎉 All systems operational!${NC}"
    echo ""
    echo "✅ Ready to use OpenWebUI MCP Cloud!"
    echo ""
    echo "📋 Service URLs:"
    echo "   GitHub (Enhanced):    http://localhost:8102"
    echo "   Filesystem (Enhanced): http://localhost:8107"
    echo "   Search:               http://localhost:8105"
    echo "   Memory:               http://localhost:8106"
    echo ""
    echo "🔧 Add these to OpenWebUI Settings > Tools"
else
    echo -e "${RED}❌ Some issues detected${NC}"
    echo ""
    echo "🔧 Common fixes:"
    echo "   1. Check Docker is running"
    echo "   2. Run: ./start-enhanced.sh"
    echo "   3. Configure .env file"
    echo "   4. Check logs: docker-compose -f docker-compose.enhanced.yml logs"
    echo ""
    echo "📖 For more help, see TROUBLESHOOTING.md"
fi

echo ""
echo "🔍 For detailed logs, run:"
echo "   docker-compose -f docker-compose.enhanced.yml logs -f"

exit $OVERALL_HEALTH