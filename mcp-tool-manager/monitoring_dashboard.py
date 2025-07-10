"""
MCP Monitoring Dashboard - Production Ready
Real-time monitoring and metrics for MCP tools
"""
import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List
import logging
from dataclasses import dataclass, asdict
from collections import deque, defaultdict

logger = logging.getLogger(__name__)

@dataclass
class ToolMetric:
    """Metric data point for a tool"""
    timestamp: datetime
    tool_name: str
    operation: str
    response_time: float
    success: bool
    error: str = None
    
class MCPDashboard:
    """Real-time monitoring dashboard for MCP tools"""
    
    def __init__(self, tool_manager, cache_manager):
        self.tool_manager = tool_manager
        self.cache_manager = cache_manager
        
        # Metrics storage (in-memory for now, could be persisted)
        self.metrics_window = 3600  # Keep 1 hour of metrics
        self.metrics = defaultdict(lambda: deque(maxlen=10000))
        
        # Aggregated stats
        self.stats = {
            'total_requests': 0,
            'total_errors': 0,
            'start_time': datetime.now()
        }
        
    def record_metric(self, metric: ToolMetric):
        """Record a metric data point"""
        self.metrics[metric.tool_name].append(metric)
        
        # Update global stats
        self.stats['total_requests'] += 1
        if not metric.success:
            self.stats['total_errors'] += 1
            
    def get_metrics(self, time_range_minutes: int = 60) -> Dict[str, Any]:
        """Get comprehensive metrics for all tools"""
        cutoff_time = datetime.now() - timedelta(minutes=time_range_minutes)
        
        metrics = {
            'summary': self._get_summary_metrics(),
            'tools': {},
            'system': self._get_system_metrics(),
            'alerts': self._check_alerts()
        }
        
        # Per-tool metrics
        for tool_name in self.tool_manager.tools:
            metrics['tools'][tool_name] = self._get_tool_metrics(tool_name, cutoff_time)
            
        return metrics
        
    def _get_summary_metrics(self) -> Dict[str, Any]:
        """Get overall system summary"""
        uptime = datetime.now() - self.stats['start_time']
        
        return {
            'uptime_seconds': uptime.total_seconds(),
            'total_requests': self.stats['total_requests'],
            'total_errors': self.stats['total_errors'],
            'overall_success_rate': (
                (self.stats['total_requests'] - self.stats['total_errors']) / 
                max(self.stats['total_requests'], 1)
            ),
            'requests_per_minute': self.stats['total_requests'] / max(uptime.total_seconds() / 60, 1)
        }
        
    def _get_tool_metrics(self, tool_name: str, cutoff_time: datetime) -> Dict[str, Any]:
        """Get metrics for a specific tool"""
        tool_metrics = [m for m in self.metrics[tool_name] if m.timestamp > cutoff_time]
        
        if not tool_metrics:
            return {
                'status': 'idle',
                'requests': 0
            }
            
        # Calculate statistics
        response_times = [m.response_time for m in tool_metrics if m.success]
        errors = [m for m in tool_metrics if not m.success]
        
        # Group by operation
        operations = defaultdict(list)
        for metric in tool_metrics:
            operations[metric.operation].append(metric)
            
        return {
            'status': 'healthy' if len(errors) / len(tool_metrics) < 0.1 else 'degraded',
            'requests': len(tool_metrics),
            'errors': len(errors),
            'success_rate': (len(tool_metrics) - len(errors)) / len(tool_metrics),
            'avg_response_time': sum(response_times) / len(response_times) if response_times else 0,
            'p95_response_time': self._calculate_percentile(response_times, 95),
            'p99_response_time': self._calculate_percentile(response_times, 99),
            'requests_per_minute': len(tool_metrics) / max((datetime.now() - cutoff_time).total_seconds() / 60, 1),
            'operations': {
                op: {
                    'count': len(metrics),
                    'avg_time': sum(m.response_time for m in metrics if m.success) / 
                               max(sum(1 for m in metrics if m.success), 1)
                }
                for op, metrics in operations.items()
            },
            'recent_errors': [
                {
                    'timestamp': e.timestamp.isoformat(),
                    'operation': e.operation,
                    'error': e.error
                }
                for e in errors[-5:]  # Last 5 errors
            ]
        }
        
    def _get_system_metrics(self) -> Dict[str, Any]:
        """Get system-level metrics"""
        return {
            'active_tools': len(self.tool_manager.tools),
            'healthy_tools': sum(
                1 for tool in self.tool_manager.tools.values() 
                if tool.is_healthy
            ),
            'cache_stats': asyncio.create_task(self.cache_manager.get_stats()),
            'queue_depth': self.tool_manager.metrics.get('queue_depth', 0)
        }
        
    def _check_alerts(self) -> List[Dict[str, Any]]:
        """Check for alert conditions"""
        alerts = []
        
        # Check each tool
        for tool_name, tool in self.tool_manager.tools.items():
            # High error rate alert
            tool_metrics = self._get_tool_metrics(tool_name, datetime.now() - timedelta(minutes=5))
            
            if tool_metrics['requests'] > 10 and tool_metrics['success_rate'] < 0.9:
                alerts.append({
                    'level': 'warning',
                    'tool': tool_name,
                    'message': f"High error rate: {(1 - tool_metrics['success_rate']) * 100:.1f}%",
                    'timestamp': datetime.now().isoformat()
                })
                
            # Slow response alert
            if tool_metrics['p95_response_time'] > 5.0:
                alerts.append({
                    'level': 'warning',
                    'tool': tool_name,
                    'message': f"Slow responses: P95 = {tool_metrics['p95_response_time']:.2f}s",
                    'timestamp': datetime.now().isoformat()
                })
                
        # System-level alerts
        summary = self._get_summary_metrics()
        if summary['overall_success_rate'] < 0.95:
            alerts.append({
                'level': 'critical',
                'tool': 'system',
                'message': f"System-wide error rate high: {(1 - summary['overall_success_rate']) * 100:.1f}%",
                'timestamp': datetime.now().isoformat()
            })
            
        return alerts
        
    def _calculate_percentile(self, values: List[float], percentile: int) -> float:
        """Calculate percentile value"""
        if not values:
            return 0
            
        sorted_values = sorted(values)
        index = int((percentile / 100) * len(sorted_values))
        return sorted_values[min(index, len(sorted_values) - 1)]
        
    async def export_metrics(self, format: str = 'prometheus') -> str:
        """Export metrics in various formats"""
        metrics = self.get_metrics()
        
        if format == 'prometheus':
            return self._export_prometheus(metrics)
        elif format == 'json':
            return json.dumps(metrics, indent=2, default=str)
        else:
            raise ValueError(f"Unknown export format: {format}")
            
    def _export_prometheus(self, metrics: Dict[str, Any]) -> str:
        """Export metrics in Prometheus format"""
        lines = []
        
        # Summary metrics
        summary = metrics['summary']
        lines.append(f"mcp_uptime_seconds {summary['uptime_seconds']}")
        lines.append(f"mcp_total_requests {summary['total_requests']}")
        lines.append(f"mcp_total_errors {summary['total_errors']}")
        lines.append(f"mcp_success_rate {summary['overall_success_rate']}")
        
        # Per-tool metrics
        for tool_name, tool_metrics in metrics['tools'].items():
            if tool_metrics['requests'] == 0:
                continue
                
            lines.append(f'mcp_tool_requests{{tool="{tool_name}"}} {tool_metrics["requests"]}')
            lines.append(f'mcp_tool_errors{{tool="{tool_name}"}} {tool_metrics["errors"]}')
            lines.append(f'mcp_tool_success_rate{{tool="{tool_name}"}} {tool_metrics["success_rate"]}')
            lines.append(f'mcp_tool_response_time_avg{{tool="{tool_name}"}} {tool_metrics["avg_response_time"]}')
            lines.append(f'mcp_tool_response_time_p95{{tool="{tool_name}"}} {tool_metrics["p95_response_time"]}')
            
        return '\n'.join(lines)

class DashboardServer:
    """HTTP server for dashboard metrics"""
    
    def __init__(self, dashboard: MCPDashboard, port: int = 9090):
        self.dashboard = dashboard
        self.port = port
        
    async def start(self):
        """Start metrics HTTP server"""
        from aiohttp import web
        
        app = web.Application()
        app.router.add_get('/metrics', self.handle_metrics)
        app.router.add_get('/dashboard', self.handle_dashboard)
        app.router.add_get('/health', self.handle_health)
        
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, '0.0.0.0', self.port)
        await site.start()
        
        logger.info(f"Dashboard server started on port {self.port}")
        
    async def handle_metrics(self, request):
        """Prometheus metrics endpoint"""
        from aiohttp import web
        
        metrics = await self.dashboard.export_metrics('prometheus')
        return web.Response(text=metrics, content_type='text/plain')
        
    async def handle_dashboard(self, request):
        """JSON dashboard endpoint"""
        from aiohttp import web
        
        metrics = self.dashboard.get_metrics()
        return web.json_response(metrics)
        
    async def handle_health(self, request):
        """Health check endpoint"""
        from aiohttp import web
        
        health = {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'tools': {}
        }
        
        for tool_name, tool in self.dashboard.tool_manager.tools.items():
            health['tools'][tool_name] = await tool.health_check()
            
        return web.json_response(health)

# Example usage
async def main():
    # Simulated dashboard (would use real tool manager in production)
    class MockToolManager:
        tools = {'github': None, 'desktop-commander': None}
        metrics = {'queue_depth': 5}
    
    class MockCacheManager:
        async def get_stats(self):
            return {'hit_rate': 0.85}
    
    dashboard = MCPDashboard(MockToolManager(), MockCacheManager())
    
    # Record some metrics
    dashboard.record_metric(ToolMetric(
        timestamp=datetime.now(),
        tool_name='github',
        operation='search_repositories',
        response_time=0.5,
        success=True
    ))
    
    # Get metrics
    metrics = dashboard.get_metrics()
    print(json.dumps(metrics, indent=2, default=str))
    
    # Start server
    server = DashboardServer(dashboard)
    await server.start()
    
    # Keep running
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
