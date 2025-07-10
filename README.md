# OpenWebUI MCP Cloud - Enhanced Setup

A production-ready integration of OpenWebUI with Model Context Protocol (MCP) tools, featuring intelligent wrappers for seamless GitHub and filesystem operations.

## 🚀 Features

### Enhanced GitHub Integration
- **Auto-Owner Injection**: Automatically injects "Insta-Bids-System" as repository owner
- **Smart Error Handling**: Fixes common GitHub API issues
- **Transparent Proxying**: Works with existing OpenWebUI GitHub tools

### Enhanced Filesystem Integration  
- **Auto-Path Normalization**: Converts `"."` → `"/workspace"` automatically
- **Tool Redirection**: Routes wrong tools to correct filesystem operations
- **Workspace Management**: Ensures all file operations use proper paths

### Additional MCP Services
- **Search**: Brave Search integration for web queries
- **Memory**: Persistent memory for AI conversations
- **Modular Architecture**: Easy to extend with new MCP services

## 🏗️ Architecture

```
OpenWebUI
    ↓
Enhanced Wrappers (Ports 8102, 8107)
    ↓
Core MCP Services (Ports 8104, 8105, 8106)
    ↓
External APIs (GitHub, Brave Search, etc.)
```

## 📋 Prerequisites

### Required Software
- **Docker** (v20.10+) and **Docker Compose** (v2.0+)
- **OpenWebUI** instance running
- **Git** for repository management

### API Keys Required
- **GitHub Personal Access Token** (for repository operations)
- **Brave Search API Key** (optional, for web search)

### System Requirements
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 10GB free space
- **Network**: Internet access for API calls

## 🔧 Installation

### 1. Clone Repository
```bash
git clone https://github.com/yourusername/openwebui-mcp-cloud.git
cd openwebui-mcp-cloud
```

### 2. Configure Environment
```bash
# Copy example environment file
cp .env.example .env

# Edit with your API keys
nano .env
```

### 3. Set Up API Keys

#### GitHub Token Setup
1. Go to [GitHub Settings > Developer settings > Personal access tokens](https://github.com/settings/tokens)
2. Click "Generate new token (classic)"
3. Select scopes: `repo`, `read:user`, `user:email`
4. Copy token to `.env` file

#### Brave Search API Key (Optional)
1. Go to [Brave Search API](https://api.search.brave.com/)
2. Sign up and get API key
3. Add to `.env` file

## 🚀 Quick Start

### 1. Start Enhanced MCP Services
```bash
# Start all services with enhanced wrappers
./start-enhanced.sh
```

### 2. Configure OpenWebUI
1. Open OpenWebUI in your browser
2. Go to **Settings > Tools**
3. Add the following MCP servers:

| Service | URL | Description |
|---------|-----|-------------|
| GitHub (Enhanced) | `http://localhost:8102` | GitHub operations with auto-owner injection |
| Filesystem (Enhanced) | `http://localhost:8107` | File operations with auto-path normalization |
| Search | `http://localhost:8105` | Web search capabilities |
| Memory | `http://localhost:8106` | Persistent AI memory |

### 3. Test Integration
```bash
# Test GitHub wrapper
curl -s http://localhost:8102/openapi.json | jq .info.title

# Test filesystem wrapper
curl -s http://localhost:8107/openapi.json | jq .info.title

# Run comprehensive tests
./test-filesystem-wrapper.sh
```

## 📖 Usage Examples

### GitHub Operations
```
User: "List my repositories"
→ Wrapper automatically adds "Insta-Bids-System" as owner
→ Shows repositories for that account

User: "Create a new repository called 'test-repo'"
→ Wrapper handles authentication and owner injection
→ Creates repository under correct account
```

### Filesystem Operations
```
User: "List files in my directory"
→ Wrapper converts "." to "/workspace"
→ Shows files in correct workspace location

User: "Read the contents of config.json"
→ Wrapper converts to "/workspace/config.json"
→ Reads from correct location
```

## 🛠️ Advanced Configuration

### Custom Workspace Path
```yaml
# docker-compose.enhanced.yml
services:
  local-mcpo-filesystem:
    volumes:
      - ./data/custom-workspace:/workspace  # Custom path
```

### Additional MCP Services
```yaml
# Add new MCP service
services:
  custom-mcp-service:
    image: ghcr.io/open-webui/mcpo:main
    command: ["mcpo", "--service", "custom-service"]
    ports:
      - "8108:8000"
```

### Environment Variables
```bash
# Core Configuration
GITHUB_TOKEN=your_github_token_here
BRAVE_SEARCH_API_KEY=your_brave_search_key_here

# MCP Authentication
MCP_API_KEY=local-mcp-key-for-testing

# Custom Settings
WORKSPACE_BASE=/workspace
GITHUB_DEFAULT_OWNER=Insta-Bids-System
```

## 🔍 Monitoring & Debugging

### View Service Logs
```bash
# All services
docker-compose -f docker-compose.enhanced.yml logs -f

# Specific service
docker-compose -f docker-compose.enhanced.yml logs -f github-wrapper
docker-compose -f docker-compose.enhanced.yml logs -f filesystem-wrapper
```

### Health Checks
```bash
# Check all services
./scripts/health-check.sh

# Manual health check
services=("8102" "8107" "8104" "8105" "8106")
for port in "${services[@]}"; do
    curl -s http://localhost:$port/openapi.json > /dev/null && echo "Port $port: OK" || echo "Port $port: FAILED"
done
```

### Common Issues

#### Service Not Starting
```bash
# Check Docker status
docker-compose -f docker-compose.enhanced.yml ps

# Check logs for errors
docker-compose -f docker-compose.enhanced.yml logs service-name
```

#### GitHub Authentication Errors
```bash
# Verify token in .env
cat .env | grep GITHUB_TOKEN

# Test token manually
curl -H "Authorization: Bearer $GITHUB_TOKEN" https://api.github.com/user
```

#### Filesystem Path Issues
```bash
# Check workspace directory
ls -la ./data/workspace/

# Verify wrapper is normalizing paths
docker-compose -f docker-compose.enhanced.yml logs filesystem-wrapper | grep "Path normalized"
```

## 🧪 Testing

### Automated Tests
```bash
# Test filesystem wrapper
./test-filesystem-wrapper.sh

# Test GitHub wrapper
./test-github-tools.sh

# Test all endpoints
./test-mcp-endpoints.sh
```

### Manual Testing
```bash
# Test filesystem path normalization
curl -X POST http://localhost:8107/list_directory \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer local-mcp-key-for-testing" \
  -d '{"path": "."}'

# Test GitHub owner injection
curl -X POST http://localhost:8102/search_repositories \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer local-mcp-key-for-testing" \
  -d '{"query": "test"}'
```

## 📁 Project Structure

```
openwebui-mcp-cloud/
├── mcp-github-wrapper/          # GitHub wrapper with auto-owner injection
│   ├── main.py
│   ├── Dockerfile
│   └── requirements.txt
├── mcp-filesystem-wrapper/      # Filesystem wrapper with path normalization
│   ├── main.py
│   ├── Dockerfile
│   └── requirements.txt
├── docker-compose.enhanced.yml  # Enhanced setup with both wrappers
├── start-enhanced.sh           # Start all enhanced services
├── stop-enhanced.sh            # Stop all services
├── test-filesystem-wrapper.sh  # Test filesystem wrapper
├── data/
│   └── workspace/              # Workspace directory for file operations
└── scripts/                    # Utility scripts
```

## 🔒 Security

### API Key Management
- Store API keys in `.env` file (never commit to Git)
- Use environment variables for production deployment
- Rotate keys regularly

### Network Security
- Services communicate over internal Docker network
- Only necessary ports exposed to host
- Consider using reverse proxy for production

### Access Control
- MCP services use API key authentication
- Configure OpenWebUI user permissions appropriately
- Monitor service logs for suspicious activity

## 🚀 Production Deployment

### Docker Compose Production
```bash
# Use production configuration
docker-compose -f docker-compose.production.yml up -d

# With custom environment
docker-compose -f docker-compose.production.yml --env-file .env.production up -d
```

### Environment-Specific Configs
```bash
# Development
cp .env.example .env.development

# Staging  
cp .env.example .env.staging

# Production
cp .env.example .env.production
```

## 🤝 Contributing

### Development Setup
```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest tests/

# Format code
black mcp-*-wrapper/
```

### Adding New MCP Services
1. Create new wrapper directory: `mcp-newservice-wrapper/`
2. Implement service logic in `main.py`
3. Add to `docker-compose.enhanced.yml`
4. Update documentation

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

### Getting Help
- **Issues**: [GitHub Issues](https://github.com/yourusername/openwebui-mcp-cloud/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/openwebui-mcp-cloud/discussions)
- **Documentation**: This README and inline code comments

### Troubleshooting Resources
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Common issues and solutions
- [TOOL_TROUBLESHOOTING.md](TOOL_TROUBLESHOOTING.md) - Tool-specific problems
- Service logs: `docker-compose logs -f service-name`

---

## 🌟 What Makes This Special

This setup provides a **production-ready foundation** for OpenWebUI + MCP integration with:

- **Zero-Configuration AI**: Wrappers handle all the complexity
- **Bulletproof Operations**: Automatic error handling and path normalization  
- **Transparent Integration**: Works with existing OpenWebUI workflows
- **Comprehensive Logging**: Full visibility into all operations
- **Scalable Architecture**: Easy to extend with new services

**Perfect for teams who want powerful AI tools without the complexity!** 🎯
