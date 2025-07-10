"""
Unified MCP Tool Manager - Production-Ready Abstraction Layer
Handles intelligent routing, fallbacks, and context-aware tool selection
"""
import asyncio
import json
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ToolType(Enum):
    LOCAL = "desktop-commander"
    GITHUB = "github"
    REMOTE = "droplet-executor"

@dataclass
class Operation:
    type: str
    path: Optional[str] = None
    content: Optional[str] = None
    params: Dict[str, Any] = None
    context: Dict[str, Any] = None

class ToolWrapper:
    """Base wrapper for MCP tools"""
    def __init__(self, tool_name: str, endpoint: str):
        self.tool_name = tool_name
        self.endpoint = endpoint
        self.health_check_interval = 30
        self.is_healthy = True
        
    async def execute(self, operation: Operation) -> Dict[str, Any]:
        """Execute operation with automatic retry and error handling"""
        max_retries = 3
        retry_delay = 1
        
        for attempt in range(max_retries):
            try:
                result = await self._execute_internal(operation)
                return result
            except Exception as e:
                logger.warning(f"{self.tool_name} attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay * (attempt + 1))
                else:
                    raise
                    
    async def _execute_internal(self, operation: Operation) -> Dict[str, Any]:
        """Override in subclasses"""
        raise NotImplementedError
        
    async def health_check(self) -> bool:
        """Check if the tool is responsive"""
        try:
            # Implement health check logic
            return True
        except:
            return False

class MCPToolManager:
    """Production-ready tool manager with intelligent routing and fallbacks"""
    
    def __init__(self):
        self.tools = {}
        self.context_analyzer = ContextAnalyzer()
        self.fallback_chain = {}
        self.metrics = ToolMetrics()
        
    def register_tool(self, tool_type: ToolType, wrapper: ToolWrapper):
        """Register a tool wrapper"""
        self.tools[tool_type] = wrapper
        logger.info(f"Registered tool: {tool_type.value}")
        
    def set_fallback_chain(self, primary: ToolType, fallbacks: List[ToolType]):
        """Define fallback order for tools"""
        self.fallback_chain[primary] = fallbacks
        
    async def execute(self, operation: Operation, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Smart execution with automatic tool selection and fallbacks
        """
        # Determine the best tool for the operation
        tool_type = self.context_analyzer.determine_tool(operation, context)
        
        # Track metrics
        start_time = asyncio.get_event_loop().time()
        
        try:
            # Primary tool execution
            result = await self._execute_with_fallback(tool_type, operation)
            
            # Record success metrics
            self.metrics.record_success(tool_type, asyncio.get_event_loop().time() - start_time)
            
            return self._format_response(result, tool_type)
            
        except Exception as e:
            # Record failure metrics
            self.metrics.record_failure(tool_type, str(e))
            
            # Handle failure gracefully
            return self._handle_failure(operation, e)
            
    async def _execute_with_fallback(self, tool_type: ToolType, operation: Operation) -> Dict[str, Any]:
        """Execute with automatic fallback to alternate tools"""
        tools_to_try = [tool_type]
        
        # Add fallback tools if defined
        if tool_type in self.fallback_chain:
            tools_to_try.extend(self.fallback_chain[tool_type])
            
        last_error = None
        
        for current_tool in tools_to_try:
            if current_tool not in self.tools:
                continue
                
            try:
                logger.info(f"Attempting execution with {current_tool.value}")
                tool = self.tools[current_tool]
                
                # Check tool health before execution
                if not tool.is_healthy:
                    logger.warning(f"Tool {current_tool.value} is unhealthy, skipping")
                    continue
                    
                result = await tool.execute(operation)
                logger.info(f"Successfully executed with {current_tool.value}")
                return result
                
            except Exception as e:
                logger.error(f"Failed with {current_tool.value}: {e}")
                last_error = e
                
        # All tools failed
        raise Exception(f"All tools failed. Last error: {last_error}")
        
    def _format_response(self, result: Dict[str, Any], tool_type: ToolType) -> Dict[str, Any]:
        """Format response with metadata"""
        return {
            "success": True,
            "tool": tool_type.value,
            "result": result,
            "timestamp": asyncio.get_event_loop().time()
        }
        
    def _handle_failure(self, operation: Operation, error: Exception) -> Dict[str, Any]:
        """Handle failure gracefully with helpful error messages"""
        return {
            "success": False,
            "error": str(error),
            "operation": operation.type,
            "suggestion": self._get_error_suggestion(error)
        }
        
    def _get_error_suggestion(self, error: Exception) -> str:
        """Provide helpful suggestions based on error type"""
        error_msg = str(error).lower()
        
        if "permission" in error_msg:
            return "Check file permissions or run with appropriate privileges"
        elif "not found" in error_msg:
            return "Verify the path exists and is accessible"
        elif "timeout" in error_msg:
            return "The operation timed out. Try again or check network connectivity"
        else:
            return "An unexpected error occurred. Check logs for details"

class ContextAnalyzer:
    """Intelligently determine which tool to use based on context"""
    
    def __init__(self):
        self.patterns = {
            ToolType.LOCAL: [
                'test', 'local', 'desktop', 'development', 'debug',
                'localhost', 'dev environment', 'workspace'
            ],
            ToolType.GITHUB: [
                'repository', 'repo', 'commit', 'push', 'pull request',
                'branch', 'merge', 'github', 'version control'
            ],
            ToolType.REMOTE: [
                'deploy', 'production', 'server', 'droplet', 'cloud',
                'staging', 'live', 'remote'
            ]
        }
        
    def determine_tool(self, operation: Operation, context: Optional[Dict[str, Any]] = None) -> ToolType:
        """Determine the best tool for the operation"""
        
        # Check explicit context hints
        if context and 'tool_preference' in context:
            return ToolType(context['tool_preference'])
            
        # Analyze operation type
        if operation.type == 'file_write':
            return self._determine_file_destination(operation.path)
        elif operation.type == 'code_execution':
            return self._determine_execution_environment(operation, context)
        elif operation.type in ['search', 'list']:
            return self._determine_search_target(operation, context)
            
        # Analyze content and context for patterns
        return self._analyze_patterns(operation, context)
        
    def _determine_file_destination(self, path: str) -> ToolType:
        """Determine where a file should be written"""
        if not path:
            return ToolType.LOCAL
            
        # Config files often go to production
        config_extensions = ['.conf', '.yml', '.yaml', '.env', '.json']
        if any(path.endswith(ext) for ext in config_extensions):
            if 'production' in path or 'prod' in path:
                return ToolType.REMOTE
                
        # Test files run locally
        if 'test' in path or 'spec' in path:
            return ToolType.LOCAL
            
        # Source code goes to repository
        code_extensions = ['.py', '.js', '.ts', '.java', '.go', '.rs']
        if any(path.endswith(ext) for ext in code_extensions):
            return ToolType.GITHUB
            
        # Default to local
        return ToolType.LOCAL
        
    def _determine_execution_environment(self, operation: Operation, context: Dict[str, Any]) -> ToolType:
        """Determine where code should be executed"""
        if context and 'environment' in context:
            env = context['environment'].lower()
            if env in ['production', 'prod', 'staging']:
                return ToolType.REMOTE
            elif env in ['development', 'dev', 'local']:
                return ToolType.LOCAL
                
        # Default to local for safety
        return ToolType.LOCAL
        
    def _determine_search_target(self, operation: Operation, context: Dict[str, Any]) -> ToolType:
        """Determine where to search"""
        search_query = operation.params.get('query', '') if operation.params else ''
        
        if any(keyword in search_query.lower() for keyword in ['repo', 'repository', 'github']):
            return ToolType.GITHUB
        elif any(keyword in search_query.lower() for keyword in ['server', 'droplet', 'production']):
            return ToolType.REMOTE
        else:
            return ToolType.LOCAL
            
    def _analyze_patterns(self, operation: Operation, context: Dict[str, Any]) -> ToolType:
        """Analyze patterns in operation and context"""
        # Combine all text for analysis
        text_to_analyze = []
        
        if operation.type:
            text_to_analyze.append(operation.type)
        if operation.path:
            text_to_analyze.append(operation.path)
        if operation.content:
            text_to_analyze.append(operation.content[:200])  # First 200 chars
        if context:
            text_to_analyze.append(json.dumps(context))
            
        combined_text = ' '.join(text_to_analyze).lower()
        
        # Score each tool based on pattern matches
        scores = {}
        for tool_type, patterns in self.patterns.items():
            score = sum(1 for pattern in patterns if pattern in combined_text)
            scores[tool_type] = score
            
        # Return tool with highest score
        if scores:
            return max(scores, key=scores.get)
            
        # Default to local
        return ToolType.LOCAL

class ToolMetrics:
    """Track metrics for monitoring and optimization"""
    
    def __init__(self):
        self.metrics = {
            'requests': {},
            'response_times': {},
            'errors': {},
            'success_rate': {}
        }
        
    def record_success(self, tool_type: ToolType, response_time: float):
        """Record successful execution"""
        tool_name = tool_type.value
        
        if tool_name not in self.metrics['requests']:
            self.metrics['requests'][tool_name] = 0
            self.metrics['response_times'][tool_name] = []
            self.metrics['errors'][tool_name] = 0
            
        self.metrics['requests'][tool_name] += 1
        self.metrics['response_times'][tool_name].append(response_time)
        
        # Keep only last 100 response times
        if len(self.metrics['response_times'][tool_name]) > 100:
            self.metrics['response_times'][tool_name] = self.metrics['response_times'][tool_name][-100:]
            
    def record_failure(self, tool_type: ToolType, error: str):
        """Record failed execution"""
        tool_name = tool_type.value
        
        if tool_name not in self.metrics['errors']:
            self.metrics['errors'][tool_name] = 0
            
        self.metrics['errors'][tool_name] += 1
        
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics"""
        result = {}
        
        for tool_name in self.metrics['requests']:
            total_requests = self.metrics['requests'][tool_name]
            total_errors = self.metrics['errors'].get(tool_name, 0)
            response_times = self.metrics['response_times'][tool_name]
            
            result[tool_name] = {
                'total_requests': total_requests,
                'total_errors': total_errors,
                'success_rate': (total_requests - total_errors) / total_requests if total_requests > 0 else 0,
                'avg_response_time': sum(response_times) / len(response_times) if response_times else 0,
                'p95_response_time': sorted(response_times)[int(len(response_times) * 0.95)] if response_times else 0
            }
            
        return result

# Example usage
if __name__ == "__main__":
    # Initialize manager
    manager = MCPToolManager()
    
    # Register tools
    # manager.register_tool(ToolType.LOCAL, DesktopCommanderWrapper())
    # manager.register_tool(ToolType.GITHUB, GitHubWrapper())
    # manager.register_tool(ToolType.REMOTE, DropletExecutorWrapper())
    
    # Set fallback chains
    manager.set_fallback_chain(ToolType.REMOTE, [ToolType.LOCAL])
    
    # Example operation
    operation = Operation(
        type="file_write",
        path="/app/config/production.yml",
        content="# Production config"
    )
    
    # Execute with automatic tool selection
    # result = await manager.execute(operation)
