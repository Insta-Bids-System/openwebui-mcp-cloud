"""
GitHub MCP Wrapper - Production Ready
Handles GitHub operations with intelligent defaults and error recovery
"""
import os
import asyncio
import aiohttp
import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import re

logger = logging.getLogger(__name__)

class GitHubWrapper:
    """Enhanced wrapper for GitHub MCP tool with intelligent defaults"""
    
    def __init__(self, endpoint: str = "http://localhost:8102"):
        self.endpoint = endpoint
        self.session = None
        self.default_owner = os.environ.get('GITHUB_DEFAULT_OWNER', 'Insta-Bids-System')
        self.rate_limiter = RateLimiter()
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
            
    async def execute(self, operation) -> Dict[str, Any]:
        """Execute GitHub operation with intelligent parameter injection"""
        
        # Apply rate limiting
        await self.rate_limiter.acquire()
        
        # Inject default owner if needed
        if hasattr(operation, 'params') and operation.params:
            operation.params = self._inject_defaults(operation.params, operation.type)
            
        # Execute operation
        result = await self._execute_github_operation(operation)
        
        # Handle rate limit headers
        if 'headers' in result:
            self.rate_limiter.update_from_headers(result['headers'])
            
        return result
        
    def _inject_defaults(self, params: Dict[str, Any], operation_type: str) -> Dict[str, Any]:
        """Intelligently inject default parameters"""
        
        # Operations that need owner injection
        owner_operations = [
            'create_repository', 'get_repository', 'update_repository',
            'create_issue', 'update_issue', 'create_pull_request',
            'get_file_contents', 'create_or_update_file', 'delete_file'
        ]
        
        if operation_type in owner_operations and 'owner' not in params:
            params['owner'] = self.default_owner
            logger.info(f"Injected default owner: {self.default_owner}")
            
        # Smart query modifications for search operations
        if operation_type == 'search_repositories' and 'query' in params:
            params['query'] = self._enhance_search_query(params['query'])
            
        # Default branch handling
        if 'branch' in params and not params.get('branch'):
            params['branch'] = 'main'  # Modern default
            
        return params
        
    def _enhance_search_query(self, query: str) -> str:
        """Enhance search queries with context"""
        
        # If searching for "my" repos, add user filter
        if re.search(r'\bmy\b', query, re.IGNORECASE):
            query = re.sub(r'\bmy\b', '', query, flags=re.IGNORECASE)
            query = f"user:{self.default_owner} {query}".strip()
            
        # If no user/org specified and looks like personal search
        personal_indicators = ['list', 'show', 'all']
        if any(indicator in query.lower() for indicator in personal_indicators):
            if f"user:{self.default_owner}" not in query:
                query = f"user:{self.default_owner} {query}"
                
        return query.strip()
        
    async def _execute_github_operation(self, operation) -> Dict[str, Any]:
        """Execute the actual GitHub MCP operation"""
        
        # Map operation types to endpoints
        endpoint_map = {
            'search_repositories': '/search_repositories',
            'create_repository': '/create_repository',
            'get_repository': '/get_repository',
            'update_repository': '/update_repository',
            'delete_repository': '/delete_repository',
            'list_issues': '/list_issues',
            'create_issue': '/create_issue',
            'update_issue': '/update_issue',
            'list_pull_requests': '/list_pull_requests',
            'create_pull_request': '/create_pull_request',
            'merge_pull_request': '/merge_pull_request',
            'get_file_contents': '/get_file_contents',
            'create_or_update_file': '/create_or_update_file',
            'delete_file': '/delete_file',
            'push_files': '/push_files'
        }
        
        endpoint = endpoint_map.get(operation.type)
        if not endpoint:
            raise ValueError(f"Unknown operation type: {operation.type}")
            
        try:
            async with self.session.post(
                f"{self.endpoint}{endpoint}",
                json=getattr(operation, 'params', {}),
                headers={'Authorization': f"Bearer {os.environ.get('MCP_API_KEY', '')}"},
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                result = await response.json()
                
                # Add response headers for rate limiting
                result['headers'] = dict(response.headers)
                
                if response.status == 200:
                    return {'success': True, **result}
                else:
                    return {
                        'success': False,
                        'error': result.get('error', 'Unknown error'),
                        'status': response.status,
                        'headers': dict(response.headers)
                    }
                    
        except asyncio.TimeoutError:
            return {'success': False, 'error': 'Operation timed out'}
        except Exception as e:
            logger.error(f"GitHub operation failed: {e}")
            return {'success': False, 'error': str(e)}
            
    async def create_repository_with_template(self, name: str, description: str = "", 
                                            template: str = "basic") -> Dict[str, Any]:
        """Create repository with common template files"""
        
        # Create the repository
        create_op = type('Operation', (), {
            'type': 'create_repository',
            'params': {
                'name': name,
                'description': description,
                'private': False,
                'auto_init': True
            }
        })()
        
        result = await self.execute(create_op)
        if not result.get('success'):
            return result
            
        # Add template files based on template type
        template_files = self._get_template_files(template)
        
        # Push template files
        push_op = type('Operation', (), {
            'type': 'push_files',
            'params': {
                'repo': name,
                'branch': 'main',
                'files': template_files,
                'message': f'Initial commit with {template} template'
            }
        })()
        
        return await self.execute(push_op)
        
    def _get_template_files(self, template: str) -> List[Dict[str, str]]:
        """Get template files for different project types"""
        
        templates = {
            'basic': [
                {
                    'path': 'README.md',
                    'content': '# Project Name\n\nProject description here.\n\n## Getting Started\n\n...'
                },
                {
                    'path': '.gitignore',
                    'content': '# Common ignores\n*.log\n*.tmp\n.env\nnode_modules/\n__pycache__/\n'
                }
            ],
            'python': [
                {
                    'path': 'README.md',
                    'content': '# Python Project\n\n## Setup\n\n```bash\npip install -r requirements.txt\n```'
                },
                {
                    'path': 'requirements.txt',
                    'content': '# Add your dependencies here\n'
                },
                {
                    'path': '.gitignore',
                    'content': '__pycache__/\n*.py[cod]\n*$py.class\n.env\nvenv/\n'
                },
                {
                    'path': 'main.py',
                    'content': '#!/usr/bin/env python3\n\ndef main():\n    print("Hello, World!")\n\nif __name__ == "__main__":\n    main()\n'
                }
            ],
            'node': [
                {
                    'path': 'README.md',
                    'content': '# Node.js Project\n\n## Setup\n\n```bash\nnpm install\n```'
                },
                {
                    'path': 'package.json',
                    'content': json.dumps({
                        "name": "project-name",
                        "version": "1.0.0",
                        "description": "",
                        "main": "index.js",
                        "scripts": {
                            "start": "node index.js",
                            "test": "echo \"Error: no test specified\" && exit 1"
                        },
                        "license": "MIT"
                    }, indent=2)
                },
                {
                    'path': '.gitignore',
                    'content': 'node_modules/\n*.log\n.env\ndist/\n'
                },
                {
                    'path': 'index.js',
                    'content': 'console.log("Hello, World!");\n'
                }
            ]
        }
        
        return templates.get(template, templates['basic'])
        
    async def smart_commit(self, repo: str, files: List[Dict[str, str]], 
                          message: str = None) -> Dict[str, Any]:
        """Smart commit with automatic message generation"""
        
        if not message:
            # Generate commit message based on files
            if len(files) == 1:
                action = "Update" if files[0].get('exists') else "Add"
                message = f"{action} {files[0]['path']}"
            else:
                message = f"Update {len(files)} files"
                
        operation = type('Operation', (), {
            'type': 'push_files',
            'params': {
                'repo': repo,
                'files': files,
                'message': message,
                'branch': 'main'
            }
        })()
        
        return await self.execute(operation)
        
    async def health_check(self) -> bool:
        """Check if GitHub MCP is responsive"""
        try:
            operation = type('Operation', (), {
                'type': 'search_repositories',
                'params': {'query': 'test', 'per_page': 1}
            })()
            result = await self.execute(operation)
            return result.get('success', False)
        except:
            return False

class RateLimiter:
    """Handle GitHub API rate limiting"""
    
    def __init__(self):
        self.remaining = 5000  # Default GitHub limit
        self.reset_time = None
        self.limit = 5000
        
    async def acquire(self):
        """Wait if rate limit is close to exhaustion"""
        if self.remaining < 10 and self.reset_time:
            wait_time = self.reset_time - datetime.now().timestamp()
            if wait_time > 0:
                logger.warning(f"Rate limit low, waiting {wait_time:.0f}s")
                await asyncio.sleep(wait_time)
                
    def update_from_headers(self, headers: Dict[str, str]):
        """Update rate limit info from response headers"""
        if 'X-RateLimit-Remaining' in headers:
            self.remaining = int(headers['X-RateLimit-Remaining'])
        if 'X-RateLimit-Reset' in headers:
            self.reset_time = int(headers['X-RateLimit-Reset'])
        if 'X-RateLimit-Limit' in headers:
            self.limit = int(headers['X-RateLimit-Limit'])
            
        logger.debug(f"Rate limit: {self.remaining}/{self.limit}")

# Example usage
async def main():
    async with GitHubWrapper() as wrapper:
        # Search for repositories (will auto-inject user if "my" is used)
        operation = type('Operation', (), {
            'type': 'search_repositories',
            'params': {'query': 'my python projects'}
        })()
        
        result = await wrapper.execute(operation)
        print(f"Search result: {result}")
        
        # Create repository with template
        result = await wrapper.create_repository_with_template(
            name="test-project",
            description="Test project with template",
            template="python"
        )
        print(f"Create result: {result}")

if __name__ == "__main__":
    asyncio.run(main())
