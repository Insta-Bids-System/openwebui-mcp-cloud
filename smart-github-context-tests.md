# Smart GitHub Context Tests

## 🧠 Testing Context-Aware GitHub Parameter Selection

### ✅ GLOBAL SEARCHES (No Owner Parameter)

#### Test 1: Popular Repository Search
**Prompt**: "Find me 3 Python repositories with 100K+ stars"
**Expected Behavior**:
- Tool: `tool_search_repositories_post`
- Parameters: `{"query": "language:python stars:>100000"}`
- **NO owner parameter** - searches ALL of GitHub

#### Test 2: Technology Search  
**Prompt**: "Show me popular React component libraries on GitHub"
**Expected Behavior**:
- Tool: `tool_search_repositories_post`
- Parameters: `{"query": "react components library stars:>1000"}`
- **NO owner parameter** - global search

#### Test 3: Specific User Search
**Prompt**: "Find repositories by Facebook on GitHub"
**Expected Behavior**:
- Tool: `tool_search_repositories_post`
- Parameters: `{"query": "user:facebook"}`
- **NO hardcoded owner** - searches Facebook's repos

### ✅ MY REPOSITORY WORK (With "Insta-Bids-System" Owner)

#### Test 4: Work with Known Repo
**Prompt**: "Create a project-status.md file in our openwebui-mcp-test repository"
**Expected Behavior**:
- Tool: `tool_create_or_update_file_post`
- Parameters: 
```json
{
  "owner": "Insta-Bids-System",
  "repo": "openwebui-mcp-test", 
  "path": "project-status.md",
  "content": "...",
  "branch": "main"
}
```

#### Test 5: Dynamic Repo Name
**Prompt**: "Create a README.md in my new-project repository"
**Expected Behavior**:
- Tool: `tool_create_or_update_file_post`
- Parameters:
```json
{
  "owner": "Insta-Bids-System",
  "repo": "new-project",
  "path": "README.md", 
  "content": "...",
  "branch": "main"
}
```

#### Test 6: Collaborative Context
**Prompt**: "Look at the README in our openwebui-mcp-test repo"
**Expected Behavior**:
- Tool: `tool_get_file_contents_post`
- Parameters:
```json
{
  "owner": "Insta-Bids-System",
  "repo": "openwebui-mcp-test",
  "path": "README.md"
}
```

## 🔍 Context Recognition Patterns

### Triggers for "Insta-Bids-System" Owner:
- "our repo", "my repo", "our project"
- "openwebui-mcp-test" (known repo name)
- "create", "update", "add to" (when referring to user's work)
- Collaborative language: "our", "we", "the project"

### Triggers for Global Search (No Owner):
- "popular", "top", "best", "find repos with X stars"
- "search GitHub for", "look for projects"
- References to other users/organizations
- General discovery language

## 📊 Success Criteria

### ✅ Intelligent Parameter Selection:
- Global searches: No owner parameter
- My repos: owner = "Insta-Bids-System" 
- Dynamic repo names from context
- Correct branch defaulting to "main"

### ✅ Context Understanding:
- Distinguishes "find popular" vs "work with mine"
- Extracts repo names from user input
- Recognizes collaborative pronouns ("our", "my")
- Handles both discovery and management tasks

### ❌ Common Failures to Avoid:
- Using repo name as owner: `"owner": "openwebui-mcp-test"`
- Hardcoding owner for global searches
- Missing owner for personal repo work
- Using "master" instead of "main" branch

## 🎯 Real-World Test Scenarios

### Scenario 1: Development Workflow
1. **"Find some good GitHub Actions examples"** → Global search
2. **"Create .github/workflows/ci.yml in our openwebui-mcp-test"** → Use owner
3. **"Look at how Microsoft does CI/CD"** → Global search of Microsoft repos

### Scenario 2: Research and Implementation  
1. **"Search for Docker Compose examples with 1000+ stars"** → Global search
2. **"Update our docker-compose.yml based on what I found"** → Use owner
3. **"Check what's in our current docker setup"** → Use owner

This demonstrates the AI can intelligently switch between global GitHub discovery and personal repository management! 