# 🚀 Quick Start Guide

Get OpenWebUI + MCP tools running in **5 minutes**!

## 1. Prerequisites

- **Docker** installed and running
- **GitHub Personal Access Token** ([Get one here](https://github.com/settings/tokens))
- **OpenWebUI** running (if not, [install it](https://docs.openwebui.com/))

## 2. Clone & Configure

```bash
# Clone the repository
git clone https://github.com/yourusername/openwebui-mcp-cloud.git
cd openwebui-mcp-cloud

# Copy minimal environment file
cp .env.minimal .env

# Edit .env with your GitHub token
nano .env
```

**In `.env`, replace:**
```
GITHUB_TOKEN=your_github_token_here
```
**With your actual GitHub token**

## 3. Start Services

```bash
# Start enhanced MCP services
./start-enhanced.sh
```

Wait for all services to start (about 30 seconds).

## 4. Configure OpenWebUI

1. Open OpenWebUI in your browser
2. Go to **Settings** → **Tools**
3. Add these two MCP servers:

| Name | URL | 
|------|-----|
| **Enhanced GitHub** | `http://localhost:8102` |
| **Enhanced Filesystem** | `http://localhost:8107` |

## 5. Test It!

Try these commands in OpenWebUI:

### Test GitHub Integration
```
"List my repositories"
"Create a new repository called test-repo"
```

### Test Filesystem Integration  
```
"List files in my directory"
"Create a file called hello.txt with some content"
```

## 🎉 Done!

You now have:
- ✅ **Smart GitHub tools** with auto-owner injection
- ✅ **Smart filesystem tools** with auto-path normalization  
- ✅ **Web search** capabilities (if you added Brave API key)
- ✅ **Persistent memory** for your AI

## 🔧 Optional: Add Search

For web search capabilities:
1. Get a free API key from [Brave Search](https://api.search.brave.com/)
2. Add it to your `.env` file:
   ```
   BRAVE_SEARCH_API_KEY=your_brave_key_here
   ```
3. Restart: `./stop-enhanced.sh && ./start-enhanced.sh`
4. Add to OpenWebUI Tools: `http://localhost:8105`

## 🆘 Need Help?

- **Services not starting?** Check `docker-compose -f docker-compose.enhanced.yml logs`
- **GitHub errors?** Verify your token has `repo` scope
- **Files not found?** The filesystem wrapper auto-converts paths to `/workspace`

## 📖 Next Steps

- Read the full [README.md](README.md) for advanced configuration
- Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common issues
- Explore the [examples](examples/) directory for more use cases

---

**That's it! You're ready to use AI-powered GitHub and filesystem tools!** 🎯
