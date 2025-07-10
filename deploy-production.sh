#!/bin/bash
# Production Deployment Script for MCP Tools
# This script handles the complete deployment process

set -e  # Exit on error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
REGISTRY="${DOCKER_REGISTRY:-docker.io/insta-bids-system}"
VERSION="${VERSION:-latest}"
STACK_NAME="${STACK_NAME:-mcp-prod}"

echo -e "${GREEN}🚀 MCP Production Deployment Script${NC}"
echo "Registry: $REGISTRY"
echo "Version: $VERSION"
echo "Stack: $STACK_NAME"
echo ""

# Function to check prerequisites
check_prerequisites() {
    echo -e "${YELLOW}Checking prerequisites...${NC}"
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}❌ Docker not found. Please install Docker.${NC}"
        exit 1
    fi
    
    # Check if Docker Swarm is initialized
    if ! docker info | grep -q "Swarm: active"; then
        echo -e "${YELLOW}Initializing Docker Swarm...${NC}"
        docker swarm init
    fi
    
    # Check environment variables
    required_vars=("MCP_API_KEY" "GITHUB_TOKEN" "POSTGRES_USER" "POSTGRES_PASSWORD")
    for var in "${required_vars[@]}"; do
        if [ -z "${!var}" ]; then
            echo -e "${RED}❌ Required environment variable $var is not set${NC}"
            exit 1
        fi
    done
    
    echo -e "${GREEN}✅ All prerequisites met${NC}"
}

# Function to build and push images
build_and_push() {
    echo -e "${YELLOW}Building and pushing Docker images...${NC}"
    
    # Build tool manager image
    cd mcp-tool-manager
    docker build -t $REGISTRY/mcp-tool-manager:$VERSION .
    docker push $REGISTRY/mcp-tool-manager:$VERSION
    cd ..
    
    # Build other images if needed
    # Add more build commands here
    
    echo -e "${GREEN}✅ Images built and pushed${NC}"
}

# Function to create secrets
create_secrets() {
    echo -e "${YELLOW}Creating Docker secrets...${NC}"
    
    # Create secrets if they don't exist
    echo "$MCP_API_KEY" | docker secret create mcp-api-key - 2>/dev/null || true
    echo "$GITHUB_TOKEN" | docker secret create github-token - 2>/dev/null || true
    echo "$POSTGRES_PASSWORD" | docker secret create postgres-password - 2>/dev/null || true
    
    if [ -n "$DO_API_TOKEN" ]; then
        echo "$DO_API_TOKEN" | docker secret create do-api-token - 2>/dev/null || true
    fi
    
    echo -e "${GREEN}✅ Secrets created${NC}"
}

# Function to create configs
create_configs() {
    echo -e "${YELLOW}Creating Docker configs...${NC}"
    
    # Create nginx config
    cat > /tmp/nginx.conf <<EOF
events {
    worker_connections 1024;
}

http {
    upstream desktop-commander {
        least_conn;
        server desktop-commander:8000 max_fails=3 fail_timeout=30s;
    }
    
    upstream github-mcp {
        least_conn;
        server github-mcp:8000 max_fails=3 fail_timeout=30s;
    }
    
    server {
        listen 80;
        
        location /desktop/ {
            proxy_pass http://desktop-commander/;
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
        }
        
        location /github/ {
            proxy_pass http://github-mcp/;
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
        }
        
        location /health {
            return 200 "healthy\n";
        }
    }
}
EOF
    
    docker config create mcp-nginx-config-v1 /tmp/nginx.conf 2>/dev/null || true
    rm /tmp/nginx.conf
    
    echo -e "${GREEN}✅ Configs created${NC}"
}

# Function to deploy stack
deploy_stack() {
    echo -e "${YELLOW}Deploying stack...${NC}"
    
    # Set environment variables for deployment
    export REGISTRY
    export VERSION
    export POSTGRES_USER
    export GITHUB_DEFAULT_OWNER="${GITHUB_DEFAULT_OWNER:-Insta-Bids-System}"
    
    # Deploy the stack
    docker stack deploy -c docker-compose.production-swarm.yml $STACK_NAME
    
    echo -e "${GREEN}✅ Stack deployed${NC}"
}

# Function to wait for services
wait_for_services() {
    echo -e "${YELLOW}Waiting for services to be ready...${NC}"
    
    # Wait up to 5 minutes for services to be ready
    timeout=300
    elapsed=0
    
    while [ $elapsed -lt $timeout ]; do
        # Check if all services have at least one running replica
        not_ready=$(docker service ls --filter "label=com.docker.stack.namespace=$STACK_NAME" \
            --format "{{.Replicas}}" | grep -c "0/")
        
        if [ $not_ready -eq 0 ]; then
            echo -e "${GREEN}✅ All services are ready${NC}"
            return 0
        fi
        
        echo -ne "\rWaiting... ($elapsed/$timeout seconds)"
        sleep 5
        elapsed=$((elapsed + 5))
    done
    
    echo -e "${RED}❌ Services did not become ready in time${NC}"
    return 1
}

# Function to run health checks
run_health_checks() {
    echo -e "${YELLOW}Running health checks...${NC}"
    
    # Get gateway service endpoint
    gateway_ip=$(docker service inspect ${STACK_NAME}_mcp-gateway \
        --format '{{range .Endpoint.VirtualIPs}}{{.Addr}}{{end}}' | cut -d'/' -f1)
    
    if [ -z "$gateway_ip" ]; then
        echo -e "${RED}❌ Could not find gateway IP${NC}"
        return 1
    fi
    
    # Check health endpoint
    if curl -sf http://$gateway_ip/health > /dev/null; then
        echo -e "${GREEN}✅ Health check passed${NC}"
    else
        echo -e "${RED}❌ Health check failed${NC}"
        return 1
    fi
    
    # Check individual services
    for service in desktop github; do
        if curl -sf http://$gateway_ip/$service/health > /dev/null; then
            echo -e "${GREEN}✅ $service service healthy${NC}"
        else
            echo -e "${YELLOW}⚠️  $service service not responding yet${NC}"
        fi
    done
}

# Function to show deployment info
show_info() {
    echo -e "${GREEN}🎉 Deployment Complete!${NC}"
    echo ""
    echo "Stack Name: $STACK_NAME"
    echo "Services:"
    docker service ls --filter "label=com.docker.stack.namespace=$STACK_NAME"
    echo ""
    echo "To view logs:"
    echo "  docker service logs ${STACK_NAME}_desktop-commander"
    echo "  docker service logs ${STACK_NAME}_github-mcp"
    echo ""
    echo "To scale services:"
    echo "  docker service scale ${STACK_NAME}_desktop-commander=6"
    echo ""
    echo "To remove stack:"
    echo "  docker stack rm $STACK_NAME"
}

# Main deployment flow
main() {
    echo -e "${GREEN}Starting MCP Production Deployment${NC}"
    echo "======================================="
    
    check_prerequisites
    build_and_push
    create_secrets
    create_configs
    deploy_stack
    wait_for_services
    run_health_checks
    show_info
    
    echo -e "${GREEN}✅ Deployment successful!${NC}"
}

# Run main function
main "$@"