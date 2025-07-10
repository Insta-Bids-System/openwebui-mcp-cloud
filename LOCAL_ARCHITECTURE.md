# Local MCP Testing Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Your Windows Machine                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────┐      http://localhost:8080           │
│  │   Web Browser   │─────────────────┐                    │
│  └─────────────────┘                 ▼                    │
│                           ┌──────────────────────┐         │
│                           │   OpenWebUI (8080)   │         │
│                           │  - Chat Interface    │         │
│                           │  - Tool Management   │         │
│                           └──────────┬───────────┘         │
│                                      │                      │
│                    ┌─────────────────┴─────────────────┐   │
│                    │        Internal Calls             │   │
│                    ▼                                   ▼   │
│  ┌─────────────────────────────────────────────────────┐  │
│  │              MCPO Bridge Layer                       │  │
│  ├─────────────────────────────────────────────────────┤  │
│  │ :8101 - OpenWebUI Tools  │ :8104 - Brave Search     │  │
│  │ :8102 - GitHub Tools     │ :8105 - Memory/Knowledge │  │
│  │ :8103 - Filesystem Tools │                          │  │
│  └─────────────────┬───────────────────────────────────┘  │
│                    │                                        │
│                    ▼                                        │
│  ┌─────────────────────────────────────────────────────┐  │
│  │              MCP Servers (npm packages)              │  │
│  ├─────────────────────────────────────────────────────┤  │
│  │ • Your custom mcp_server (165 tools)                │  │
│  │ • @modelcontextprotocol/server-github               │  │
│  │ • @modelcontextprotocol/server-filesystem           │  │
│  │ • @modelcontextprotocol/server-brave-search         │  │
│  │ • @modelcontextprotocol/server-memory               │  │
│  └─────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐  │
│  │              Data Storage (Docker Volumes)           │  │
│  ├─────────────────────────────────────────────────────┤  │
│  │ • PostgreSQL (local)    • Redis (local)             │  │
│  │ • ./data/workspace      • ./data/memory             │  │
│  │ • ./data/openwebui                                  │  │
│  └─────────────────────────────────────────────────────┘  │
│                                                             │
└─────────────────────────────────────────────────────────────┘

## Port Mapping

External (Browser) → Internal (Docker)
- localhost:8080 → open-webui:8080
- localhost:8101 → mcpo-openwebui:8000
- localhost:8102 → mcpo-github:8000
- localhost:8103 → mcpo-filesystem:8000
- localhost:8104 → mcpo-brave-search:8000
- localhost:8105 → mcpo-memory:8000
- localhost:4000 → litellm:4000 (optional)

## Network Flow

1. User interacts with OpenWebUI at localhost:8080
2. OpenWebUI makes HTTP/OpenAPI calls to MCPO bridges
3. MCPO converts to MCP protocol and calls actual MCP servers
4. Results flow back through MCPO to OpenWebUI
5. User sees results in chat interface

All services communicate on internal 'local-ai-net' Docker network.
