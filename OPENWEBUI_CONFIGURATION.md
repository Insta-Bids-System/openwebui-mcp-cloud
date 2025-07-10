# OpenWebUI Configuration for MCP Tools

## Settings → Personalization → System Prompt

Add this ENTIRE block to your system prompt:

```
You have access to MCP tools for filesystem, GitHub, and memory operations.

FILESYSTEM TOOL RULES - CRITICAL:
1. When creating files: Use path="filename.txt" (NEVER "/app/filename.txt")
2. When reading files: Use path="filename.txt" (NEVER "/app/filename.txt")
3. When listing directories: Use path="." or path="/workspace/"
4. When creating folders: Use path="foldername" (NEVER "/app/foldername")

Examples of CORRECT usage:
- write_file with path="test.txt" ✓
- read_file with path="docs/readme.md" ✓
- list_directory with path="." ✓

Examples of WRONG usage:
- write_file with path="/app/test.txt" ✗
- read_file with path="C:\\Users\\test.txt" ✗
- list_directory with path="/" ✗

If you get "path outside allowed directories" error, you used the wrong path format.
```

## Settings → Models → Model Settings

For EACH model (GPT-4, Gemini, etc.), add to "Model Instructions":

```
Filesystem paths must be relative: "file.txt" not "/app/file.txt"
```

## Create Conversation Templates

Save these as templates in Settings → Prompts:

### Template: "Create File"
```
Create a file named {{filename}} with the following content: {{content}}
Note: Use path="{{filename}}" when calling write_file, not "/app/{{filename}}"
```

### Template: "Read File"
```
Read the contents of {{filename}}
Note: Use path="{{filename}}" when calling read_file
```

### Template: "List Files"
```
List all files in the workspace
Note: Use path="." or path="/workspace/" when calling list_directory
```