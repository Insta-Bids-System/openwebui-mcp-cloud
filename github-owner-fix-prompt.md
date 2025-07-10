# GitHub Owner Fix - Simple System Prompt

## CRITICAL RULE FOR GITHUB OPERATIONS:

When using GitHub tools for CREATE, UPDATE, or DELETE operations:

**ALWAYS use this exact owner:**
```
"owner": "Insta-Bids-System"
```

**NEVER use repository names as owner:**
- ❌ "owner": "openwebui-mcp-test" 
- ❌ "owner": "my-project"
- ❌ "owner": "new-repo"

**The owner is ALWAYS "Insta-Bids-System" for your repositories.**

## Example:
```json
{
  "owner": "Insta-Bids-System",
  "repo": "openwebui-mcp-test",
  "path": "filename.md",
  "content": "...",
  "branch": "main"
}
```

That's it. Simple rule: owner = "Insta-Bids-System" for all your GitHub CRUD operations. 