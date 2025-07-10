# Preset Prompts for MCP Tools

## File Operations

### Create File
```
Please create a new file with the write_file tool using these exact parameters:
- path: "{{FILENAME}}"
- content: "{{CONTENT}}"
Do not add /app/ or any other prefix to the path.
```

### Read File
```
Please read the file using read_file tool with:
- path: "{{FILENAME}}"
```

### List Files
```
Please list all files using list_directory tool with:
- path: "."
```

### Create Project Structure
```
Please create the following project structure:
1. Use create_directory with path="src"
2. Use create_directory with path="tests"
3. Use create_directory with path="docs"
4. Use write_file with path="src/main.py" and content="# Main application"
5. Use write_file with path="README.md" and content="# Project README"
```

## GitHub Operations

### List Repositories
```
Use the GitHub tool to list all repositories for the authenticated user
```

### Create Repository
```
Use the GitHub tool to create a new repository with:
- name: "{{REPO_NAME}}"
- description: "{{DESCRIPTION}}"
- private: false
```

## Memory Operations

### Store Information
```
Use the memory tool to remember: {{INFORMATION}}
```

### Recall Information
```
Use the memory tool to recall what you know about: {{TOPIC}}
```