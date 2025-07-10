"""
MCP Cache Manager - Production Ready
Distributed caching layer for MCP operations
"""
import json
import asyncio
import aioredis
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import hashlib
import logging

logger = logging.getLogger(__name__)

class MCPCacheManager:
    """Distributed cache manager for MCP operations"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self.redis = None
        self.cache_ttl = {
            # GitHub operations
            'github_repo_info': 3600,        # 1 hour
            'github_search': 600,            # 10 minutes
            'github_file_contents': 300,     # 5 minutes
            
            # Desktop Commander operations
            'file_contents': 300,            # 5 minutes  
            'directory_listings': 600,       # 10 minutes
            'file_info': 1800,              # 30 minutes
            
            # General operations
            'health_check': 60,              # 1 minute
            'user_preferences': 3600,        # 1 hour
            'tool_metrics': 120              # 2 minutes
        }
        
    async def connect(self):
        """Connect to Redis"""
        self.redis = await aioredis.create_redis_pool(
            self.redis_url,
            encoding='utf-8'
        )
        
    async def close(self):
        """Close Redis connection"""
        if self.redis:
            self.redis.close()
            await self.redis.wait_closed()
            
    def _generate_cache_key(self, tool: str, operation: str, params: Dict[str, Any]) -> str:
        """Generate deterministic cache key"""
        # Sort params for consistent hashing
        params_str = json.dumps(params, sort_keys=True)
        key_data = f"{tool}:{operation}:{params_str}"
        
        # Use hash for shorter keys
        key_hash = hashlib.sha256(key_data.encode()).hexdigest()[:16]
        return f"mcp:{tool}:{operation}:{key_hash}"
        
    async def get(self, tool: str, operation: str, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get cached result if available and not expired"""
        if not self.redis:
            return None
            
        key = self._generate_cache_key(tool, operation, params)
        
        try:
            cached_data = await self.redis.get(key)
            if cached_data:
                data = json.loads(cached_data)
                logger.debug(f"Cache hit for {key}")
                return data
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            
        return None
        
    async def set(self, tool: str, operation: str, params: Dict[str, Any], 
                  result: Dict[str, Any], ttl: Optional[int] = None):
        """Cache operation result"""
        if not self.redis:
            return
            
        key = self._generate_cache_key(tool, operation, params)
        
        # Determine TTL
        if ttl is None:
            operation_key = f"{tool}_{operation}"
            ttl = self.cache_ttl.get(operation_key, 300)  # Default 5 minutes
            
        try:
            await self.redis.setex(
                key,
                ttl,
                json.dumps(result)
            )
            logger.debug(f"Cached {key} for {ttl}s")
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            
    async def invalidate(self, tool: str, operation: Optional[str] = None):
        """Invalidate cache entries"""
        if not self.redis:
            return
            
        pattern = f"mcp:{tool}:*"
        if operation:
            pattern = f"mcp:{tool}:{operation}:*"
            
        try:
            # Find all matching keys
            keys = []
            cursor = 0
            while True:
                cursor, partial_keys = await self.redis.scan(
                    cursor, match=pattern, count=100
                )
                keys.extend(partial_keys)
                if cursor == 0:
                    break
                    
            # Delete all matching keys
            if keys:
                await self.redis.delete(*keys)
                logger.info(f"Invalidated {len(keys)} cache entries")
        except Exception as e:
            logger.error(f"Cache invalidation error: {e}")
            
    async def get_or_execute(self, tool: str, operation: str, params: Dict[str, Any],
                           executor, force_fresh: bool = False) -> Dict[str, Any]:
        """Cache-first execution strategy"""
        
        # Check cache first unless forced fresh
        if not force_fresh:
            cached = await self.get(tool, operation, params)
            if cached:
                return cached
                
        # Execute operation
        result = await executor()
        
        # Cache successful results
        if result.get('success'):
            await self.set(tool, operation, params, result)
            
        return result
        
    async def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        if not self.redis:
            return {'error': 'Redis not connected'}
            
        try:
            info = await self.redis.info()
            keys = await self.redis.dbsize()
            
            return {
                'connected': True,
                'total_keys': keys,
                'memory_used': info.get('used_memory_human', 'N/A'),
                'hit_rate': info.get('keyspace_hits', 0) / 
                           (info.get('keyspace_hits', 0) + info.get('keyspace_misses', 1)),
                'uptime_seconds': info.get('uptime_in_seconds', 0)
            }
        except Exception as e:
            logger.error(f"Failed to get cache stats: {e}")
            return {'error': str(e)}

class CacheWarmer:
    """Pre-warm cache with common operations"""
    
    def __init__(self, cache_manager: MCPCacheManager, tool_manager):
        self.cache = cache_manager
        self.tools = tool_manager
        
    async def warm_common_operations(self):
        """Pre-warm cache with frequently used operations"""
        
        warming_tasks = [
            # GitHub operations
            {
                'tool': 'github',
                'operation': 'search_repositories',
                'params': {'query': 'stars:>1000', 'per_page': 10}
            },
            {
                'tool': 'github',
                'operation': 'search_repositories', 
                'params': {'query': f'user:{self.tools.default_owner}', 'per_page': 20}
            },
            
            # Desktop Commander operations
            {
                'tool': 'desktop-commander',
                'operation': 'list_directory',
                'params': {'path': '/workspace'}
            },
            
            # Health checks
            {
                'tool': 'all',
                'operation': 'health_check',
                'params': {}
            }
        ]
        
        results = []
        for task in warming_tasks:
            try:
                if task['tool'] == 'all':
                    # Warm all tool health checks
                    for tool_name in self.tools.tools:
                        result = await self.tools.tools[tool_name].health_check()
                        await self.cache.set(
                            tool_name, 'health_check', {}, 
                            {'success': result, 'timestamp': datetime.now().isoformat()}
                        )
                else:
                    # Execute and cache specific operation
                    operation = type('Operation', (), {
                        'type': task['operation'],
                        'params': task['params']
                    })()
                    
                    tool = self.tools.tools.get(task['tool'])
                    if tool:
                        result = await tool.execute(operation)
                        await self.cache.set(
                            task['tool'], task['operation'], 
                            task['params'], result
                        )
                        
                results.append({'task': task, 'success': True})
                
            except Exception as e:
                logger.error(f"Cache warming failed for {task}: {e}")
                results.append({'task': task, 'success': False, 'error': str(e)})
                
        return results
        
    async def schedule_warming(self, interval_minutes: int = 30):
        """Schedule periodic cache warming"""
        while True:
            try:
                logger.info("Starting cache warming...")
                results = await self.warm_common_operations()
                
                success_count = sum(1 for r in results if r['success'])
                logger.info(f"Cache warming completed: {success_count}/{len(results)} successful")
                
            except Exception as e:
                logger.error(f"Cache warming error: {e}")
                
            # Wait for next warming cycle
            await asyncio.sleep(interval_minutes * 60)

# Example usage
async def main():
    # Initialize cache
    cache = MCPCacheManager()
    await cache.connect()
    
    # Example caching
    await cache.set(
        'github', 'search_repositories',
        {'query': 'python', 'per_page': 10},
        {'success': True, 'count': 100, 'items': []}
    )
    
    # Retrieve from cache
    result = await cache.get(
        'github', 'search_repositories',
        {'query': 'python', 'per_page': 10}
    )
    print(f"Cached result: {result}")
    
    # Get stats
    stats = await cache.get_stats()
    print(f"Cache stats: {stats}")
    
    await cache.close()

if __name__ == "__main__":
    asyncio.run(main())
