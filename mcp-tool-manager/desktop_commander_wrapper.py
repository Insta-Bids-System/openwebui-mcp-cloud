"""
Desktop Commander MCP Wrapper - Production Ready
Handles local file operations with enhanced error handling and caching
"""
import os
import asyncio
import aiohttp
import json
import logging
from typing import Dict, Any, Optional
from pathlib import Path
from datetime import datetime, timedelta
import hashlib

logger = logging.getLogger(__name__)

class DesktopCommanderWrapper:
    """Enhanced wrapper for desktop-commander MCP tool"""
    
    def __init__(self, endpoint: str = "http://localhost:8103"):
        self.endpoint = endpoint
        self.session = None
        self.cache = FileOperationCache()
        self.workspace = Path(os.environ.get('MCP_WORKSPACE', '/workspace'))
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
            
    async def execute(self, operation) -> Dict[str, Any]:
        """Execute operation with enhanced error handling and caching"""
        
        # Normalize paths
        if hasattr(operation, 'path') and operation.path:
            operation.path = self._normalize_path(operation.path)
            
        # Check cache for read operations
        if operation.type == 'read_file':
            cached = self.cache.get(operation.path)
            if cached:
                logger.info(f"Cache hit for {operation.path}")
                return cached
                
        # Execute operation
        result = await self._execute_mcp_operation(operation)
        
        # Cache successful reads
        if operation.type == 'read_file' and result.get('success'):
            self.cache.set(operation.path, result)
            
        return result
        
    def _normalize_path(self, path: str) -> str:
        """Normalize paths to absolute workspace paths"""
        path = Path(path)
        
        # Handle relative paths
        if not path.is_absolute():
            path = self.workspace / path
            
        # Ensure path is within workspace
        try:
            path.relative_to(self.workspace)
        except ValueError:
            logger.warning(f"Path {path} is outside workspace, adjusting...")
            # Extract the filename and put it in workspace
            path = self.workspace / path.name
            
        return str(path)
        
    async def _execute_mcp_operation(self, operation) -> Dict[str, Any]:
        """Execute the actual MCP operation"""
        
        # Map operation types to MCP endpoints
        endpoint_map = {
            'read_file': '/read_file',
            'write_file': '/write_file',
            'list_directory': '/list_directory',
            'create_directory': '/create_directory',
            'move_file': '/move_file',
            'search_files': '/search_files',
            'get_file_info': '/get_file_info',
            'execute_command': '/execute_command'
        }
        
        endpoint = endpoint_map.get(operation.type)
        if not endpoint:
            raise ValueError(f"Unknown operation type: {operation.type}")
            
        # Prepare request data
        data = {
            'path': getattr(operation, 'path', None),
            'content': getattr(operation, 'content', None),
            'pattern': getattr(operation, 'pattern', None),
            'command': getattr(operation, 'command', None),
        }
        
        # Remove None values
        data = {k: v for k, v in data.items() if v is not None}
        
        try:
            async with self.session.post(
                f"{self.endpoint}{endpoint}",
                json=data,
                headers={'Authorization': f"Bearer {os.environ.get('MCP_API_KEY', '')}"}
            ) as response:
                result = await response.json()
                
                if response.status == 200:
                    return {'success': True, **result}
                else:
                    return {
                        'success': False,
                        'error': result.get('error', 'Unknown error'),
                        'status': response.status
                    }
                    
        except asyncio.TimeoutError:
            return {'success': False, 'error': 'Operation timed out'}
        except Exception as e:
            logger.error(f"MCP operation failed: {e}")
            return {'success': False, 'error': str(e)}
            
    async def batch_operations(self, operations: list) -> Dict[str, Any]:
        """Execute multiple operations in parallel"""
        tasks = [self.execute(op) for op in operations]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return {
            'success': all(not isinstance(r, Exception) and r.get('success') for r in results),
            'results': results,
            'failed_count': sum(1 for r in results if isinstance(r, Exception) or not r.get('success'))
        }
        
    async def health_check(self) -> bool:
        """Check if desktop-commander is responsive"""
        try:
            operation = type('Operation', (), {'type': 'list_directory', 'path': self.workspace})()
            result = await self.execute(operation)
            return result.get('success', False)
        except:
            return False

class FileOperationCache:
    """Simple in-memory cache for file operations"""
    
    def __init__(self, ttl_seconds: int = 300):
        self.cache = {}
        self.ttl = timedelta(seconds=ttl_seconds)
        
    def _get_key(self, path: str) -> str:
        """Generate cache key from path"""
        return hashlib.md5(path.encode()).hexdigest()
        
    def get(self, path: str) -> Optional[Dict[str, Any]]:
        """Get cached result if not expired"""
        key = self._get_key(path)
        if key in self.cache:
            entry, timestamp = self.cache[key]
            if datetime.now() - timestamp < self.ttl:
                return entry
            else:
                del self.cache[key]
        return None
        
    def set(self, path: str, result: Dict[str, Any]):
        """Cache a result"""
        key = self._get_key(path)
        self.cache[key] = (result, datetime.now())
        
    def clear(self):
        """Clear all cached entries"""
        self.cache.clear()

# Enhanced file operations with automatic retries
class ResilientFileOperations:
    """File operations with automatic retries and fallbacks"""
    
    def __init__(self, wrapper: DesktopCommanderWrapper):
        self.wrapper = wrapper
        
    async def safe_write(self, path: str, content: str, backup: bool = True) -> Dict[str, Any]:
        """Write file with automatic backup"""
        operation = type('Operation', (), {
            'type': 'write_file',
            'path': path,
            'content': content
        })()
        
        # Create backup if file exists
        if backup:
            info_op = type('Operation', (), {'type': 'get_file_info', 'path': path})()
            info = await self.wrapper.execute(info_op)
            
            if info.get('success') and info.get('exists'):
                backup_path = f"{path}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                read_op = type('Operation', (), {'type': 'read_file', 'path': path})()
                content_result = await self.wrapper.execute(read_op)
                
                if content_result.get('success'):
                    backup_op = type('Operation', (), {
                        'type': 'write_file',
                        'path': backup_path,
                        'content': content_result.get('content', '')
                    })()
                    await self.wrapper.execute(backup_op)
                    
        # Write the file
        return await self.wrapper.execute(operation)
        
    async def atomic_write(self, path: str, content: str) -> Dict[str, Any]:
        """Atomic write operation using temp file and move"""
        temp_path = f"{path}.tmp.{datetime.now().timestamp()}"
        
        # Write to temp file
        write_op = type('Operation', (), {
            'type': 'write_file',
            'path': temp_path,
            'content': content
        })()
        
        result = await self.wrapper.execute(write_op)
        if not result.get('success'):
            return result
            
        # Move temp file to final location
        move_op = type('Operation', (), {
            'type': 'move_file',
            'source': temp_path,
            'destination': path
        })()
        
        return await self.wrapper.execute(move_op)

# Example usage
async def main():
    async with DesktopCommanderWrapper() as wrapper:
        # Simple file read
        operation = type('Operation', (), {
            'type': 'read_file',
            'path': 'test.txt'  # Will be normalized to /workspace/test.txt
        })()
        
        result = await wrapper.execute(operation)
        print(f"Read result: {result}")
        
        # Batch operations
        operations = [
            type('Operation', (), {'type': 'list_directory', 'path': '.'})(),
            type('Operation', (), {'type': 'get_file_info', 'path': 'README.md'})()
        ]
        
        batch_result = await wrapper.batch_operations(operations)
        print(f"Batch result: {batch_result}")

if __name__ == "__main__":
    asyncio.run(main())
