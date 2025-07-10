# 🍎 OpenWebUI + MCP Tools - Mac Setup Guide

This guide is specifically for setting up the OpenWebUI + MCP Tools project on macOS.

## 📋 Prerequisites

1. **macOS** (tested on macOS 10.15+)
2. **Docker Desktop** installed and running
3. **Git** (comes with Xcode Command Line Tools)
4. **Python 3** (usually pre-installed)
5. **GitHub Personal Access Token**

## 🚀 Quick Start (Mac)

### 1. Clone and Switch to Mac Branch
```bash
git clone https://github.com/YOUR_USERNAME/openwebui-mcp-cloud.git
cd openwebui-mcp-cloud
git checkout mac-development
```

### 2. Environment Setup
The `.env.mac` file is already configured with working credentials:
```bash
# The .env.mac file includes:
# - API keys for GitHub, Gemini, OpenWebUI
# - Local database configuration
# - MCP server settings
```

### 3. Start the Services
```bash
./start.sh
```

This script will:
- ✅ Check if Docker is running
- ✅ Copy `.env.mac` to `.env`
- ✅ Create necessary data directories
- ✅ Start all Docker services
- ✅ Show service status and access URLs

### 4. Access the Application
- **OpenWebUI**: http://localhost:8080
- **GitHub Tools**: http://localhost:8102
- **Filesystem Tools**: http://localhost:8103

## 🔧 Mac-Specific Scripts

### Available Commands
```bash
./start.sh              # Start all services
./stop.sh               # Stop all services  
./status.sh             # Check service status
./test-github-tools.sh  # Test GitHub MCP integration
./test-mcp-endpoints.sh # Test all MCP endpoints
```

### Setting up Tools in OpenWebUI

1. Open http://localhost:8080
2. Create admin account
3. Go to **Settings → Tools**
4. Add each MCP service:

#### GitHub Tools
- **API Base URL**: `http://localhost:8102`
- **Bearer Token**: `local-mcp-key-for-testing`
- **Auto-append /openapi.json**: ✅ ON

#### Filesystem Tools  
- **API Base URL**: `http://localhost:8103`
- **Bearer Token**: `local-mcp-key-for-testing`
- **Auto-append /openapi.json**: ✅ ON

## 🧪 Testing Your Setup

### Test GitHub Integration
```bash
./test-github-tools.sh
```

This will verify:
- ✅ GitHub MCP server is running
- ✅ Authentication works
- ✅ Repository search functionality
- ✅ Tool listing

### Test All MCP Endpoints
```bash
./test-mcp-endpoints.sh
```

This tests all 5 MCP services and shows available tools.

## 🎯 Using the Tools

### GitHub Operations (via chat)
- **Search**: "Search for Python repositories with more than 100 stars"
- **Read File**: "Get the README.md from microsoft/vscode"
- **Create Repo**: "Create a private repository called test-project"

### Filesystem Operations (via chat)
- **Create File**: "Create a file test.txt in workspace with hello world"
- **List Files**: "List all files in the workspace directory"
- **Read File**: "Read the contents of test.txt"

## 🔧 Troubleshooting (Mac)

### Docker Issues
```bash
# Check if Docker is running
docker info

# Restart Docker Desktop if needed
# Applications → Docker → Restart
```

### Port Conflicts
```bash
# Check what's using port 8080
lsof -i :8080

# Kill process if needed
kill -9 <PID>
```

### Permission Issues
```bash
# Make scripts executable
chmod +x *.sh

# Fix data directory permissions
sudo chown -R $(whoami) data/
```

### Service Logs
```bash
# View all logs
docker-compose -f docker-compose.local.yml logs -f

# View specific service logs
docker logs local-open-webui
docker logs local-mcpo-github
```

## 🆚 Differences from Windows Version

| Feature | Windows | Mac |
|---------|---------|-----|
| Scripts | `.bat` files | `.sh` files |
| Terminal | PowerShell | Bash/Zsh |
| Environment | `.env` | `.env.mac` |
| Testing | `.ps1` scripts | `.sh` scripts |

## 📁 Mac-Specific Files

```
mac-development/
├── .env.mac                 # Mac environment configuration
├── start.sh                 # Mac start script
├── stop.sh                  # Mac stop script  
├── status.sh                # Mac status checker
├── test-github-tools.sh     # GitHub testing script
├── test-mcp-endpoints.sh    # All endpoints test
└── README-MAC.md           # This file
```

## 🎉 What's Working

Based on successful testing:
- ✅ **GitHub Tools**: Search, read files, authentication working
- ✅ **Filesystem Tools**: Create, read, list files working  
- ✅ **OpenWebUI**: 165+ management tools available
- ✅ **Tool Calling**: GPT-3.5-turbo executes tools correctly
- ✅ **Persistence**: All data saved in `data/` directory

## 🚧 Known Limitations

- **GitHub Write Operations**: Need specific parameter formatting
- **Gemini Tool Calling**: Use GPT-3.5-turbo for better results
- **Memory Tools**: Need Brave API key for full functionality

## 🤝 Contributing

This Mac branch maintains compatibility with the main project while providing Mac-specific tooling. Feel free to improve the Mac experience!

---

**Happy coding on Mac! 🍎✨** 