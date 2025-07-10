"""
Integration Tests for MCP Tool Manager
Tests the complete system with all components
"""
import pytest
import asyncio
import json
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime
import os

# Import our modules
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp_tool_manager import (
    MCPToolManager, ToolType, Operation, ContextAnalyzer, ToolMetrics
)
from desktop_commander_wrapper import DesktopCommanderWrapper
from github_wrapper import GitHubWrapper
from cache_manager import MCPCacheManager

class TestMCPIntegration:
    """Integration tests for the complete MCP system"""
    
    @pytest.fixture
    async def tool_manager(self):
        """Create a configured tool manager for testing"""
        manager = MCPToolManager()
        
        # Register mock tools
        manager.register_tool(ToolType.LOCAL, Mock(spec=DesktopCommanderWrapper))
        manager.register_tool(ToolType.GITHUB, Mock(spec=GitHubWrapper))
        
        # Set up fallback chains
        manager.set_fallback_chain(ToolType.REMOTE, [ToolType.LOCAL])
        
        yield manager
        
    @pytest.fixture
    async def cache_manager(self):
        """Create a mock cache manager"""
        cache = Mock(spec=MCPCacheManager)
        cache.get = AsyncMock(return_value=None)
        cache.set = AsyncMock()
        cache.invalidate = AsyncMock()
        return cache
        
    @pytest.mark.asyncio
    async def test_automatic_tool_selection(self, tool_manager):
        """Test that the system automatically selects the right tool"""
        
        # Test file write operation
        operation = Operation(
            type="file_write",
            path="test.py",
            content="print('hello')"
        )
        
        # Mock the GitHub tool execution
        tool_manager.tools[ToolType.GITHUB].execute = AsyncMock(
            return_value={'success': True, 'url': 'https://github.com/...'}
        )
        
        result = await tool_manager.execute(operation)
        
        assert result['success'] is True
        assert result['tool'] == 'github'  # Python files should go to GitHub
        tool_manager.tools[ToolType.GITHUB].execute.assert_called_once()
        
    @pytest.mark.asyncio
    async def test_fallback_mechanism(self, tool_manager):
        """Test automatic fallback when primary tool fails"""
        
        operation = Operation(
            type="execute_command",
            command="echo 'test'",
            context={'environment': 'production'}
        )
        
        # Mock remote tool to fail
        if ToolType.REMOTE in tool_manager.tools:
            tool_manager.tools[ToolType.REMOTE].execute = AsyncMock(
                side_effect=Exception("Connection failed")
            )
        
        # Mock local tool to succeed
        tool_manager.tools[ToolType.LOCAL].execute = AsyncMock(
            return_value={'success': True, 'output': 'test'}
        )
        
        # Execute - should fallback to local
        result = await tool_manager.execute(operation)
        
        # Should have used local tool after remote failed
        assert 'test' in str(result)
        tool_manager.tools[ToolType.LOCAL].execute.assert_called()
        
    @pytest.mark.asyncio
    async def test_context_analysis(self):
        """Test context analyzer pattern matching"""
        
        analyzer = ContextAnalyzer()
        
        # Test various operations
        test_cases = [
            (Operation(type="file_write", path="config.yml"), ToolType.LOCAL),
            (Operation(type="file_write", path="production.conf"), ToolType.REMOTE),
            (Operation(type="file_write", path="test_app.py"), ToolType.LOCAL),
            (Operation(type="file_write", path="main.py"), ToolType.GITHUB),
            (Operation(type="search", params={'query': 'repository'}), ToolType.GITHUB),
            (Operation(type="search", params={'query': 'local files'}), ToolType.LOCAL),
        ]
        
        for operation, expected_tool in test_cases:
            result = analyzer.determine_tool(operation)
            assert result == expected_tool, f"Failed for {operation.type} {operation.path}"
            
    @pytest.mark.asyncio
    async def test_metrics_collection(self, tool_manager):
        """Test that metrics are properly collected"""
        
        operation = Operation(type="list", path="/workspace")
        
        # Mock successful execution
        tool_manager.tools[ToolType.LOCAL].execute = AsyncMock(
            return_value={'success': True, 'files': []}
        )
        
        # Execute operation
        await tool_manager.execute(operation)
        
        # Check metrics were recorded
        metrics = tool_manager.metrics.get_metrics()
        assert 'desktop-commander' in metrics
        assert metrics['desktop-commander']['total_requests'] == 1
        assert metrics['desktop-commander']['success_rate'] == 1.0
        
    @pytest.mark.asyncio
    async def test_batch_operations(self):
        """Test batch operation handling"""
        
        wrapper = DesktopCommanderWrapper()
        wrapper.session = Mock()
        wrapper.execute = AsyncMock(return_value={'success': True})
        
        operations = [
            type('Operation', (), {'type': 'list_directory', 'path': '/workspace'})(),
            type('Operation', (), {'type': 'read_file', 'path': 'test.txt'})(),
            type('Operation', (), {'type': 'get_file_info', 'path': 'README.md'})()
        ]
        
        result = await wrapper.batch_operations(operations)
        
        assert result['success'] is True
        assert result['failed_count'] == 0
        assert len(result['results']) == 3

class TestCacheIntegration:
    """Test caching layer integration"""
    
    @pytest.mark.asyncio
    async def test_cache_hit_flow(self):
        """Test complete flow with cache hit"""
        
        cache = MCPCacheManager()
        cache.redis = Mock()
        
        # Mock cache hit
        cached_data = json.dumps({'success': True, 'data': 'cached'})
        cache.redis.get = AsyncMock(return_value=cached_data)
        
        result = await cache.get('github', 'search_repositories', {'query': 'test'})
        
        assert result is not None
        assert result['data'] == 'cached'
        
    @pytest.mark.asyncio
    async def test_cache_miss_and_set(self):
        """Test cache miss and subsequent set"""
        
        cache = MCPCacheManager()
        cache.redis = Mock()
        
        # Mock cache miss
        cache.redis.get = AsyncMock(return_value=None)
        cache.redis.setex = AsyncMock()
        
        # Get (miss)
        result = await cache.get('github', 'search_repositories', {'query': 'test'})
        assert result is None
        
        # Set
        await cache.set(
            'github', 'search_repositories', 
            {'query': 'test'}, 
            {'success': True, 'count': 100}
        )
        
        cache.redis.setex.assert_called_once()
        
    @pytest.mark.asyncio
    async def test_cache_invalidation(self):
        """Test cache invalidation"""
        
        cache = MCPCacheManager()
        cache.redis = Mock()
        
        # Mock scan and delete
        cache.redis.scan = AsyncMock(return_value=(0, [b'mcp:github:test:123']))
        cache.redis.delete = AsyncMock()
        
        await cache.invalidate('github', 'search_repositories')
        
        cache.redis.delete.assert_called_once()

class TestMonitoringIntegration:
    """Test monitoring system integration"""
    
    def test_metric_recording(self):
        """Test metric recording and aggregation"""
        
        from monitoring_dashboard import MCPDashboard, ToolMetric
        
        # Create mock managers
        tool_manager = Mock()
        tool_manager.tools = {'github': Mock(), 'desktop-commander': Mock()}
        cache_manager = Mock()
        
        dashboard = MCPDashboard(tool_manager, cache_manager)
        
        # Record metrics
        metrics = [
            ToolMetric(
                timestamp=datetime.now(),
                tool_name='github',
                operation='search_repositories',
                response_time=0.5,
                success=True
            ),
            ToolMetric(
                timestamp=datetime.now(),
                tool_name='github',
                operation='search_repositories',
                response_time=0.7,
                success=True
            ),
            ToolMetric(
                timestamp=datetime.now(),
                tool_name='github',
                operation='create_repository',
                response_time=2.0,
                success=False,
                error='Rate limited'
            )
        ]
        
        for metric in metrics:
            dashboard.record_metric(metric)
            
        # Get aggregated metrics
        result = dashboard.get_metrics(time_range_minutes=5)
        
        assert 'github' in result['tools']
        github_metrics = result['tools']['github']
        assert github_metrics['requests'] == 3
        assert github_metrics['errors'] == 1
        assert github_metrics['success_rate'] == 2/3
        
    def test_alert_generation(self):
        """Test alert generation for anomalies"""
        
        from monitoring_dashboard import MCPDashboard, ToolMetric
        
        tool_manager = Mock()
        tool_manager.tools = {'github': Mock(is_healthy=True)}
        cache_manager = Mock()
        
        dashboard = MCPDashboard(tool_manager, cache_manager)
        
        # Record many failures
        for i in range(20):
            dashboard.record_metric(ToolMetric(
                timestamp=datetime.now(),
                tool_name='github',
                operation='test',
                response_time=0.1,
                success=i < 10  # 50% failure rate
            ))
            
        alerts = dashboard._check_alerts()
        
        # Should have alert for high error rate
        assert len(alerts) > 0
        assert any('error rate' in alert['message'].lower() for alert in alerts)

class TestEndToEndWorkflows:
    """Test complete end-to-end workflows"""
    
    @pytest.mark.asyncio
    async def test_code_development_workflow(self, tool_manager):
        """Test typical code development workflow"""
        
        # 1. Create local test file
        test_operation = Operation(
            type="file_write",
            path="test_feature.py",
            content="def test_function():\n    return 'test'"
        )
        
        # 2. Run tests locally
        run_operation = Operation(
            type="execute_command",
            command="python -m pytest test_feature.py"
        )
        
        # 3. Commit to GitHub
        commit_operation = Operation(
            type="push_files",
            params={
                'repo': 'test-project',
                'files': [{'path': 'test_feature.py', 'content': '...'}]
            }
        )
        
        # Mock executions
        tool_manager.tools[ToolType.LOCAL].execute = AsyncMock(
            return_value={'success': True}
        )
        tool_manager.tools[ToolType.GITHUB].execute = AsyncMock(
            return_value={'success': True, 'commit': 'abc123'}
        )
        
        # Execute workflow
        results = []
        for op in [test_operation, run_operation, commit_operation]:
            result = await tool_manager.execute(op)
            results.append(result)
            
        # All operations should succeed
        assert all(r['success'] for r in results)
        
    @pytest.mark.asyncio  
    async def test_production_deployment_workflow(self, tool_manager):
        """Test production deployment workflow"""
        
        # 1. Update configuration
        config_operation = Operation(
            type="file_write",
            path="/config/production.yml",
            content="# Production config",
            context={'environment': 'production'}
        )
        
        # 2. Deploy to server
        deploy_operation = Operation(
            type="execute_command",
            command="docker-compose up -d",
            context={'environment': 'production'}
        )
        
        # 3. Health check
        health_operation = Operation(
            type="execute_command",
            command="curl http://localhost/health",
            context={'environment': 'production'}
        )
        
        # Execute workflow
        for op in [config_operation, deploy_operation, health_operation]:
            result = await tool_manager.execute(op)
            assert 'error' not in result or not result.get('success', True)

# Performance tests
class TestPerformance:
    """Test system performance characteristics"""
    
    @pytest.mark.asyncio
    async def test_concurrent_operations(self, tool_manager):
        """Test handling of concurrent operations"""
        
        # Mock tool to add slight delay
        async def delayed_execute(op):
            await asyncio.sleep(0.1)
            return {'success': True}
            
        tool_manager.tools[ToolType.LOCAL].execute = delayed_execute
        
        # Execute many operations concurrently
        operations = [
            Operation(type="list", path=f"/workspace/dir{i}")
            for i in range(50)
        ]
        
        start_time = asyncio.get_event_loop().time()
        
        # Execute all operations
        tasks = [tool_manager.execute(op) for op in operations]
        results = await asyncio.gather(*tasks)
        
        end_time = asyncio.get_event_loop().time()
        duration = end_time - start_time
        
        # Should complete in reasonable time (not 50 * 0.1 = 5 seconds)
        assert duration < 2.0  # Concurrent execution
        assert all(r['success'] for r in results)
        
    @pytest.mark.asyncio
    async def test_cache_performance(self):
        """Test cache performance improvement"""
        
        cache = MCPCacheManager()
        cache.redis = Mock()
        
        # First call - cache miss
        cache.redis.get = AsyncMock(return_value=None)
        
        executor = AsyncMock(return_value={'success': True, 'data': 'fresh'})
        
        start = asyncio.get_event_loop().time()
        result1 = await cache.get_or_execute(
            'github', 'search', {'query': 'test'}, 
            executor
        )
        duration1 = asyncio.get_event_loop().time() - start
        
        # Second call - cache hit
        cache.redis.get = AsyncMock(
            return_value=json.dumps({'success': True, 'data': 'cached'})
        )
        
        start = asyncio.get_event_loop().time()
        result2 = await cache.get_or_execute(
            'github', 'search', {'query': 'test'}, 
            executor
        )
        duration2 = asyncio.get_event_loop().time() - start
        
        # Cache hit should be much faster
        assert duration2 < duration1 / 10

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
