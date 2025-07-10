// OpenWebUI Tool Calling Configuration

// In OpenWebUI, tools can be in different modes:

1. **Passive Mode** (Current Issue)
   - Tools are listed but not actively used
   - Model just explains how to use them
   - No actual function execution

2. **Active Mode** (What You Want)  
   - Model actively calls tool functions
   - Executes commands and returns results
   - Like Claude with MCP

// How to Enable Active Tool Calling:

// Option 1: Model Settings
// Go to Settings → Models → [Your Model]
// Look for:
- "Function Calling": Enable
- "Tool Use": Enable  
- "Allow Functions": Yes

// Option 2: Chat Settings
// In the chat window:
- Click gear icon
- Enable "Use Tools"
- Select which tools to use

// Option 3: System Prompt
// Add to system prompt:
"You have access to tools. When asked to perform file operations, 
CREATE or MODIFY files, you MUST use the available tools, not provide 
instructions. Actually execute the functions."

// Option 4: Use Tool-Specific Syntax
// Some models respond to:
- [[write_file: path=/workspace/test.txt, content=Hello]]
- {{filesystem.write_file("/workspace/test.txt", "Hello")}}
- @tools.filesystem.write_file(path="/workspace/test.txt")
