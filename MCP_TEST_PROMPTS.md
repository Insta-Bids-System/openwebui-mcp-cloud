# 🧪 MCP Tools Test Prompts for OpenWebUI

## Prerequisites
1. Make sure you've added all MCP tools in Settings → Tools:
   - GitHub MCP: http://localhost:8103 (API Key: local-mcp-key-for-testing)
   - Filesystem MCP: http://localhost:8104 (API Key: local-mcp-key-for-testing)
   - Memory MCP: http://localhost:8106 (API Key: local-mcp-key-for-testing)

## 📁 Filesystem Tool Tests

### Basic File Operations
1. "List all files in the workspace directory"
2. "Create a new file called test.txt with the content 'Hello from OpenWebUI!'"
3. "Read the contents of the test.txt file"
4. "Create a new directory called 'project-files'"
5. "Create a file called README.md in the project-files directory with some markdown content"

### Advanced File Operations
6. "Create a Python script called hello.py that prints 'Hello World'"
7. "List all files including those in subdirectories"
8. "Create a JSON file called config.json with some configuration data"
9. "Read the config.json file and explain its contents"
10. "Create multiple files: index.html, style.css, and script.js for a simple webpage"

## 🐙 GitHub Tool Tests

### Repository Operations
1. "List all my GitHub repositories"
2. "Show me the details of the [repo-name] repository"
3. "Create a new repository called 'test-from-openwebui' with a description"
4. "List the files in the root directory of [repo-name]"
5. "Show me the README.md file from [repo-name]"

### Issues and Pull Requests
6. "List all open issues in [repo-name]"
7. "Create a new issue in [repo-name] titled 'Test Issue from OpenWebUI'"
8. "Show me all pull requests in [repo-name]"
9. "List my starred repositories"
10. "Search for repositories related to 'machine learning'"

### Advanced GitHub Operations
11. "Show me the latest commits in [repo-name]"
12. "Create a new file called test.md in [repo-name] with some content"
13. "List all branches in [repo-name]"
14. "Show me my GitHub profile information"
15. "List repositories owned by 'openai' organization"

## 🧠 Memory Tool Tests

### Basic Memory Operations
1. "Remember that my favorite programming language is Python"
2. "What is my favorite programming language?"
3. "Store this information: Project deadline is December 31, 2024"
4. "Recall what you know about my project deadline"
5. "Remember these API endpoints: /users, /posts, /comments"

### Complex Memory Tests
6. "Save this configuration: Database: PostgreSQL, Port: 5432, User: admin"
7. "What database configuration did I share with you?"
8. "Remember this meeting schedule: Monday 9am standup, Wednesday 2pm review"
9. "What meetings do I have scheduled?"
10. "Store my project requirements: React frontend, Node.js backend, MongoDB database"

## 🔗 Combined Tool Tests (Multiple Tools)

### GitHub + Filesystem
1. "List my GitHub repositories and create a local file with their names"
2. "Read the README.md from [repo-name] on GitHub and save it locally as github-readme.md"
3. "Create a local Python script and then create a new GitHub repository for it"

### Memory + Filesystem
4. "Create a file called notes.txt with all the information you remember about me"
5. "Read the config.json file and remember its contents for later"

### All Tools Combined
6. "List my GitHub repos, save the list to a file, and remember my most starred repository"
7. "Create a project plan file, remember the key milestones, and create a GitHub issue for the first task"

## 🎯 Real-World Scenarios

### Project Setup
"I want to start a new web project. Create a local folder structure with index.html, style.css, and app.js files. Then create a new GitHub repository called 'my-web-app' and remember that this is my current active project."

### Documentation Management
"Read the README.md from my [repo-name] repository, create a local copy with some improvements, and remember the main features of this project."

### Task Management
"Create a TODO.md file with a list of tasks, create GitHub issues for each high-priority task, and remember the deadline for the project."

### Code Analysis
"List all Python files in the workspace, read their contents, and create a summary document explaining what each file does."

### Configuration Backup
"Read all .json and .yaml files in the workspace, create a backup directory, copy them there, and remember the backup location and timestamp."

## 🚀 Advanced Integration Tests

1. "Analyze my GitHub repository [repo-name], create a local report about its structure, and remember the key findings"

2. "Create a daily journal entry file with today's date, list what GitHub activities I did today, and remember this as my coding journal"

3. "Set up a new project: create local folders (src, tests, docs), create a GitHub repo with the same structure, and remember the project setup details"

4. "Create a Python script that generates a fibonacci sequence, save it locally, create a GitHub gist with it, and remember the algorithm used"

5. "Document my development environment: list all files in workspace, check my GitHub profile settings, create an environment.md file with all details, and remember my preferred setup"

## 💡 Tips for Testing

- Start with simple commands to ensure each tool works individually
- Test combined operations after confirming individual tools work
- Use the memory tool to build context across conversations
- Check the workspace directory (C:\Users\USER\Documents\openwebui-mcp\data\workspace) to verify file operations
- Monitor tool execution in the OpenWebUI interface

## 🐛 Troubleshooting

If a tool doesn't respond:
1. Check if it's enabled in Settings → Tools
2. Verify the URL and API key are correct
3. Test the tool endpoint directly: http://localhost:[port]/docs
4. Check Docker logs: `docker logs local-mcpo-[toolname]`

Remember: The GitHub operations will use the token you configured in the .env file!