# Filesystem MCP Wrapper

An intelligent proxy that enhances filesystem operations with automatic path normalization and tool redirection.

## Features

### 🔧 Auto-Path Normalization
- Converts `"."` → `"/workspace"`
- Converts `"test.txt"` → `"/workspace/test.txt"`
- Preserves existing `/workspace` paths
- Handles relative path conversion

### 🔄 Tool Redirection
- Redirects OpenWebUI control tools to filesystem MCP
- `tool_list_workspace_files_post` → `tool_list_directory_post`
- `tool_read_workspace_file_post` → `tool_read_file_post`
- `tool_write_workspace_file_post` → `tool_write_file_post`

### 📋 Request Enhancement
- Adds default `/workspace` path when missing
- Logs all transformations for debugging
- Preserves original request structure

## Architecture

```
OpenWebUI → Filesystem Wrapper (Port 8107) → Filesystem MCP (Port 8104)
```

## Usage

### With Docker Compose
```bash
docker-compose -f docker-compose.enhanced.yml up filesystem-wrapper
```

### OpenWebUI Configuration
In OpenWebUI Settings > Tools, add:
- **URL**: `http://localhost:8107`
- **Name**: Enhanced Filesystem Tools

## Example Transformations

### Path Normalization
```javascript
// Before
{ "path": "." }
// After  
{ "path": "/workspace" }

// Before
{ "path": "test.txt" }
// After
{ "path": "/workspace/test.txt" }
```

### Tool Redirection
```
/list_workspace_files → /list_directory
/read_workspace_file → /read_file
/write_workspace_file → /write_file
```

## Benefits

1. **No AI Prompt Engineering**: Infrastructure-level solution
2. **Transparent**: Works with existing tools without changes
3. **Debuggable**: Comprehensive logging of all transformations
4. **Consistent**: Eliminates path-related errors

## Environment Variables

- `MCP_API_KEY`: Authentication key (default: `local-mcp-key-for-testing`)
- `WORKSPACE_BASE`: Base workspace path (default: `/workspace`)

## Health Check

The wrapper includes a health check endpoint at `/openapi.json` to verify connectivity to the underlying filesystem MCP. 