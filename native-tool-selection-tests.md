# Native/Automatic Tool Selection Tests

## 🎯 Purpose: Test AI's ability to automatically choose correct tools without explicit instruction

These prompts test whether the AI can intelligently select and execute the right tools based on natural language requests, similar to Claude Desktop's native behavior.

## 📁 Filesystem Operations (Port 8103) - Native Selection

### Test 1: File Creation (Native)
**Prompt**: "Create a file called 'project-status.md' in the workspace with a summary of our MCP setup progress"
**Expected Behavior**: 
- AI should automatically choose `tool_write_file_post`
- Use path `/workspace/project-status.md`
- No explicit tool instruction needed

### Test 2: File Reading (Native)
**Prompt**: "What's in the test.txt file in our workspace?"
**Expected Behavior**:
- AI should automatically choose `tool_read_file_post`
- Use path `/workspace/test.txt`
- Present the file contents naturally

### Test 3: Directory Exploration (Native)
**Prompt**: "Show me what files are currently in our workspace"
**Expected Behavior**:
- AI should automatically choose `tool_list_directory_post`
- Use path `/workspace`
- Present files in a readable format

### Test 4: File Search (Native)
**Prompt**: "Find any files in workspace that contain the word 'test'"
**Expected Behavior**:
- AI should choose `tool_search_files_post` or read files to search
- Search within `/workspace`
- Report findings

## 🐙 GitHub Operations (Port 8102) - Native Selection

### Test 5: Repository Search (Native)
**Prompt**: "Find some popular React component libraries on GitHub"
**Expected Behavior**:
- AI should automatically choose `tool_search_repositories_post`
- Use appropriate search query
- Present results with stars/descriptions

### Test 6: Repository Creation (Native)
**Prompt**: "Create a new private repository called 'mcp-test-native' with a basic README"
**Expected Behavior**:
- AI should choose `tool_create_repository_post`
- Then `tool_create_or_update_file_post` for README
- Handle multi-step operation automatically

### Test 7: Code Exploration (Native)
**Prompt**: "Look at the README file in our openwebui-mcp-test repository"
**Expected Behavior**:
- AI should choose `tool_get_file_contents_post`
- Use correct owner/repo parameters
- Display README content

## 🔍 Web Search Operations (Port 8104) - Native Selection

### Test 8: Information Lookup (Native)
**Prompt**: "What's the latest news about Model Context Protocol development?"
**Expected Behavior**:
- AI should automatically choose `tool_brave_web_search_post`
- Use relevant search terms
- Summarize findings

### Test 9: Technical Research (Native)
**Prompt**: "Find documentation for setting up OpenWebUI with Docker"
**Expected Behavior**:
- AI should choose `tool_brave_web_search_post`
- Search for relevant documentation
- Present useful links and info

## 🧠 Memory Operations (Port 8105) - Native Selection

### Test 10: Knowledge Storage (Native)
**Prompt**: "Remember that we successfully set up 5 MCP servers today: OpenWebUI Control (8101), GitHub (8102), Filesystem (8103), Brave Search (8104), and Memory (8105)"
**Expected Behavior**:
- AI should choose `tool_create_entities_post` or similar
- Store this information for future reference
- Confirm storage

### Test 11: Memory Retrieval (Native)
**Prompt**: "What do you remember about our MCP server setup?"
**Expected Behavior**:
- AI should choose `tool_search_nodes_post` or similar
- Retrieve stored information
- Present relevant memories

## 🖥️ OpenWebUI Control (Port 8101) - Native Selection

### Test 12: System Information (Native)
**Prompt**: "Check if this OpenWebUI instance is healthy and show me the current configuration"
**Expected Behavior**:
- AI should choose `get_health` and `get_app_config`
- Present system status clearly
- No explicit tool naming needed

### Test 13: User Management (Native)
**Prompt**: "Show me all the users in this OpenWebUI system"
**Expected Behavior**:
- AI should choose `list_users`
- Present user information
- Handle permissions appropriately

## 🔄 Multi-Tool Operations (Cross-Server) - Native Selection

### Test 14: Research and Document (Cross-Server)
**Prompt**: "Research the latest OpenWebUI features online, then create a summary document in our workspace"
**Expected Behavior**:
- Step 1: Use Brave Search (8104) to research
- Step 2: Use Filesystem (8103) to create document
- Automatic multi-step execution

### Test 15: GitHub Analysis and Memory (Cross-Server)
**Prompt**: "Look at our openwebui-mcp-test repository, analyze what's there, and remember the key details"
**Expected Behavior**:
- Step 1: Use GitHub tools (8102) to explore repo
- Step 2: Use Memory tools (8105) to store findings
- Seamless cross-server operation

## 📊 Success Criteria

### Native Tool Selection Success:
- ✅ AI chooses correct tool without explicit instruction
- ✅ Uses appropriate parameters automatically
- ✅ Handles multi-step operations intelligently
- ✅ Provides natural language responses
- ✅ No "I cannot access tools" responses

### Native Tool Selection Failure:
- ❌ Asks user which tool to use
- ❌ Claims inability to perform actions
- ❌ Requires explicit tool naming
- ❌ Uses wrong tools for the task
- ❌ Doesn't attempt tool execution

## 🎯 Key Testing Points

1. **Intent Recognition**: Can AI understand what the user wants?
2. **Tool Selection**: Does it pick the right tool automatically?
3. **Parameter Handling**: Are paths, queries, etc. set correctly?
4. **Multi-Step Logic**: Can it chain operations across servers?
5. **Natural Response**: Does it respond conversationally, not technically?

## Expected Native Behavior Flow:
```
User: "Create a status file"
AI: "I'll create a status file for you."
AI: [Automatically selects tool_write_file_post]
AI: [Uses /workspace/status.txt path]
AI: [Executes without asking permission]
AI: "I've created the status file with your project information."
```

**NOT**:
```
User: "Create a status file" 
AI: "You need to use tool_write_file_post..."
AI: "Please specify the exact tool you want me to use..."
``` 