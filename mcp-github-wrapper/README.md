# GitHub MCP Wrapper

## Purpose
This wrapper automatically injects the default GitHub account name `Insta-Bids-System` for all GitHub operations, eliminating the need to specify the owner parameter every time.

## How It Works
1. **Sits between OpenWebUI and GitHub MCP**: Acts as a proxy
2. **Auto-injects owner for CUD operations**: Automatically adds `"owner": "Insta-Bids-System"` to CREATE/UPDATE/DELETE requests
3. **Fixes the READ bug**: Replaces `"your_username"` with correct account name for READ operations
4. **Preserves READ flexibility**: Allows reading from any GitHub account when explicitly specified
5. **Transparent proxy**: Forwards all requests to the actual GitHub MCP server

## CREATE/UPDATE/DELETE Endpoints (Auto-inject Owner)
- `create_repository` - Creates repos under Insta-Bids-System  
- `update_repository` - Updates repos under Insta-Bids-System
- `delete_repository` - Deletes repos under Insta-Bids-System
- `create_or_update_file` - Creates/updates files in Insta-Bids-System repos
- `delete_file` - Deletes files from Insta-Bids-System repos
- `create_branch`, `create_issue`, `create_pull_request` - All default to Insta-Bids-System

## READ Endpoints (Bug Fix Only)
- `list_repositories` - Can read from any account (or defaults to Insta-Bids-System if no owner specified)
- `get_repository` - Can read any public repo when owner specified
- `get_file_contents` - Can read from any repo when owner specified
- `list_files`, `list_branches`, `list_commits` - Flexible read access

## Architecture
```
OpenWebUI → GitHub Wrapper (Port 8102) → GitHub MCP (Internal) → GitHub API
```

## Benefits
1. **No more manual owner specification**: Just say "create a repo" instead of "create a repo for Insta-Bids-System"
2. **Fixes READ operations**: Automatically corrects the upstream bug
3. **Backwards compatible**: Works with existing prompts
4. **Easy configuration**: Single place to change default account

## Usage Examples

### CREATE/UPDATE/DELETE (Auto-defaults to Insta-Bids-System)
- ❌ Before: "Create a repository called test-project for Insta-Bids-System"  
- ✅ After: "Create a repository called test-project" (automatically uses Insta-Bids-System)
- ✅ "Update the README in my-project" (automatically uses Insta-Bids-System/my-project)
- ✅ "Delete the old-repo repository" (automatically deletes from Insta-Bids-System)

### READ Operations (Flexible - can specify any account)
- ✅ "List my repositories" (defaults to Insta-Bids-System)
- ✅ "List repositories for microsoft" (reads from microsoft account)
- ✅ "Get the README from facebook/react" (reads from facebook/react)
- ✅ "Show files in google/material-design-icons" (reads from google account)

## Configuration
- Default owner: `Insta-Bids-System` (configured in `main.py`)
- GitHub MCP URL: `http://local-mcpo-github-internal:8000`
- External port: `8102`

## Health Check
- `GET /health` - Check wrapper status
- `GET /` - Service information 