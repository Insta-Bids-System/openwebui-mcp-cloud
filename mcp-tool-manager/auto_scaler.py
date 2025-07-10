"""
MCP Auto-Scaler - Production Ready
Automatically scales MCP services based on load
"""
import asyncio
import docker
import logging
from typing import Dict, Any, List
from datetime import datetime, timedelta
import statistics

logger = logging.getLogger(__name__)

class MCPAutoScaler:
    """Auto-scale MCP services based on metrics"""
    
    def __init__(self, metrics_source, docker_client=None):
        self.metrics = metrics_source
        self.docker = docker_client or docker.from_env()
        
        # Scaling rules per service
        self.scaling_rules = {
            'desktop-commander': {
                'min_instances': 2,
                'max_instances': 10,
                'cpu_threshold_up': 70,
                'cpu_threshold_down': 30,
                'memory_threshold_up': 80,
                'memory_threshold_down': 40,
                'queue_threshold_up': 100,
                'queue_threshold_down': 20,
                'scale_up_increment': 2,
                'scale_down_increment': 1,
                'cooldown_seconds': 300
            },
            'github-mcp': {
                'min_instances': 1,
                'max_instances': 8,
                'cpu_threshold_up': 60,
                'cpu_threshold_down': 20,
                'memory_threshold_up': 70,
                'memory_threshold_down': 30,
                'requests_per_second_up': 10,
                'requests_per_second_down': 2,
                'scale_up_increment': 1,
                'scale_down_increment': 1,
                'cooldown_seconds': 300
            },
            'droplet-executor': {
                'min_instances': 1,
                'max_instances': 5,
                'cpu_threshold_up': 50,
                'cpu_threshold_down': 20,
                'queue_threshold_up': 50,
                'queue_threshold_down': 10,
                'scale_up_increment': 1,
                'scale_down_increment': 1,
                'cooldown_seconds': 600
            }
        }
        
        # Track last scaling actions
        self.last_scale_action = {}
        
    async def monitor_and_scale(self):
        """Main monitoring and scaling loop"""
        
        check_interval = 30  # seconds
        
        while True:
            try:
                # Get current metrics for all services
                service_metrics = await self.collect_service_metrics()
                
                # Check each service
                for service_name, rules in self.scaling_rules.items():
                    await self.check_and_scale_service(service_name, rules, service_metrics)
                    
            except Exception as e:
                logger.error(f"Auto-scaling error: {e}")
                
            await asyncio.sleep(check_interval)
            
    async def collect_service_metrics(self) -> Dict[str, Any]:
        """Collect metrics for all services"""
        
        metrics = {}
        
        # Get container stats from Docker
        for container in self.docker.containers.list():
            service_name = self._get_service_name(container)
            if not service_name:
                continue
                
            stats = container.stats(stream=False)
            
            # Calculate CPU percentage
            cpu_delta = stats['cpu_stats']['cpu_usage']['total_usage'] - \
                       stats['precpu_stats']['cpu_usage']['total_usage']
            system_delta = stats['cpu_stats']['system_cpu_usage'] - \
                          stats['precpu_stats']['system_cpu_usage']
            cpu_percent = (cpu_delta / system_delta) * len(stats['cpu_stats']['cpu_usage']['percpu_usage']) * 100
            
            # Calculate memory percentage
            memory_usage = stats['memory_stats']['usage']
            memory_limit = stats['memory_stats']['limit']
            memory_percent = (memory_usage / memory_limit) * 100
            
            if service_name not in metrics:
                metrics[service_name] = {
                    'instances': [],
                    'cpu_percentages': [],
                    'memory_percentages': []
                }
                
            metrics[service_name]['instances'].append(container.id)
            metrics[service_name]['cpu_percentages'].append(cpu_percent)
            metrics[service_name]['memory_percentages'].append(memory_percent)
            
        # Get application metrics from monitoring system
        app_metrics = await self.metrics.get_metrics()
        
        # Merge metrics
        for service_name in metrics:
            if service_name in app_metrics.get('tools', {}):
                tool_metrics = app_metrics['tools'][service_name]
                metrics[service_name].update({
                    'requests_per_second': tool_metrics.get('requests_per_minute', 0) / 60,
                    'queue_depth': tool_metrics.get('queue_depth', 0),
                    'error_rate': 1 - tool_metrics.get('success_rate', 1)
                })
                
        return metrics
        
    async def check_and_scale_service(self, service_name: str, rules: Dict[str, Any], 
                                     metrics: Dict[str, Any]):
        """Check if a service needs scaling"""
        
        if service_name not in metrics:
            logger.warning(f"No metrics found for service: {service_name}")
            return
            
        service_metrics = metrics[service_name]
        current_instances = len(service_metrics['instances'])
        
        # Check cooldown period
        if not self._can_scale(service_name, rules['cooldown_seconds']):
            return
            
        # Calculate average metrics
        avg_cpu = statistics.mean(service_metrics['cpu_percentages'])
        avg_memory = statistics.mean(service_metrics['memory_percentages'])
        queue_depth = service_metrics.get('queue_depth', 0)
        rps = service_metrics.get('requests_per_second', 0)
        
        # Determine scaling action
        scale_decision = self._decide_scaling(
            service_name, rules, current_instances,
            avg_cpu, avg_memory, queue_depth, rps
        )
        
        if scale_decision != 0:
            await self.scale_service(service_name, current_instances + scale_decision)
            
    def _decide_scaling(self, service_name: str, rules: Dict[str, Any], 
                       current_instances: int, cpu: float, memory: float,
                       queue_depth: int, rps: float) -> int:
        """Decide whether to scale up, down, or maintain current level"""
        
        # Check if we need to scale up
        scale_up_reasons = []
        
        if cpu > rules['cpu_threshold_up']:
            scale_up_reasons.append(f"CPU {cpu:.1f}% > {rules['cpu_threshold_up']}%")
            
        if memory > rules['memory_threshold_up']:
            scale_up_reasons.append(f"Memory {memory:.1f}% > {rules['memory_threshold_up']}%")
            
        if 'queue_threshold_up' in rules and queue_depth > rules['queue_threshold_up']:
            scale_up_reasons.append(f"Queue depth {queue_depth} > {rules['queue_threshold_up']}")
            
        if 'requests_per_second_up' in rules and rps > rules['requests_per_second_up']:
            scale_up_reasons.append(f"RPS {rps:.1f} > {rules['requests_per_second_up']}")
            
        if scale_up_reasons and current_instances < rules['max_instances']:
            logger.info(f"Scaling up {service_name}: {', '.join(scale_up_reasons)}")
            return min(rules['scale_up_increment'], 
                      rules['max_instances'] - current_instances)
            
        # Check if we need to scale down
        scale_down_conditions = [
            cpu < rules['cpu_threshold_down'],
            memory < rules['memory_threshold_down']
        ]
        
        if 'queue_threshold_down' in rules:
            scale_down_conditions.append(queue_depth < rules['queue_threshold_down'])
            
        if 'requests_per_second_down' in rules:
            scale_down_conditions.append(rps < rules['requests_per_second_down'])
            
        if all(scale_down_conditions) and current_instances > rules['min_instances']:
            logger.info(f"Scaling down {service_name}: Low resource usage")
            return -min(rules['scale_down_increment'],
                       current_instances - rules['min_instances'])
            
        return 0
        
    async def scale_service(self, service_name: str, target_instances: int):
        """Scale a service to target number of instances"""
        
        try:
            # For Docker Swarm
            service = self.docker.services.get(service_name)
            service.scale(target_instances)
            
            logger.info(f"Scaled {service_name} to {target_instances} instances")
            
            # Record scaling action
            self.last_scale_action[service_name] = datetime.now()
            
            # Emit scaling event for monitoring
            await self._emit_scaling_event(service_name, target_instances)
            
        except Exception as e:
            logger.error(f"Failed to scale {service_name}: {e}")
            
    def _can_scale(self, service_name: str, cooldown_seconds: int) -> bool:
        """Check if enough time has passed since last scaling"""
        
        if service_name not in self.last_scale_action:
            return True
            
        time_since_last_scale = datetime.now() - self.last_scale_action[service_name]
        return time_since_last_scale.total_seconds() > cooldown_seconds
        
    def _get_service_name(self, container) -> str:
        """Extract service name from container labels"""
        
        labels = container.labels
        
        # Docker Swarm service name
        if 'com.docker.swarm.service.name' in labels:
            return labels['com.docker.swarm.service.name']
            
        # Docker Compose service name
        if 'com.docker.compose.service' in labels:
            return labels['com.docker.compose.service']
            
        return None
        
    async def _emit_scaling_event(self, service_name: str, new_count: int):
        """Emit scaling event for monitoring/alerting"""
        
        event = {
            'timestamp': datetime.now().isoformat(),
            'service': service_name,
            'action': 'scale',
            'new_instance_count': new_count,
            'reason': 'auto-scale'
        }
        
        # Could send to monitoring system, log aggregator, etc.
        logger.info(f"Scaling event: {event}")

# Predictive scaling based on historical patterns
class PredictiveScaler:
    """Use historical data to predict scaling needs"""
    
    def __init__(self, metrics_store):
        self.metrics_store = metrics_store
        
    async def predict_load(self, service_name: str, hours_ahead: int = 1) -> Dict[str, float]:
        """Predict future load based on historical patterns"""
        
        # Get historical data for same time period
        historical_data = await self.metrics_store.get_historical_metrics(
            service_name,
            time_of_day=datetime.now() + timedelta(hours=hours_ahead),
            days_back=30
        )
        
        if not historical_data:
            return {}
            
        # Simple prediction based on historical averages
        predictions = {
            'cpu': statistics.mean([d['cpu'] for d in historical_data]),
            'memory': statistics.mean([d['memory'] for d in historical_data]),
            'requests_per_second': statistics.mean([d['rps'] for d in historical_data])
        }
        
        # Add confidence based on standard deviation
        for metric in predictions:
            values = [d[metric] for d in historical_data]
            predictions[f"{metric}_stddev"] = statistics.stdev(values) if len(values) > 1 else 0
            
        return predictions
        
    async def recommend_scaling(self, service_name: str, rules: Dict[str, Any]) -> int:
        """Recommend proactive scaling based on predictions"""
        
        predictions = await self.predict_load(service_name)
        
        if not predictions:
            return 0
            
        # Check if predicted load exceeds thresholds
        if predictions['cpu'] > rules['cpu_threshold_up']:
            return rules['scale_up_increment']
        elif predictions['requests_per_second'] > rules.get('requests_per_second_up', float('inf')):
            return rules['scale_up_increment']
            
        return 0

# Example usage
async def main():
    # Mock metrics source
    class MockMetrics:
        async def get_metrics(self):
            return {
                'tools': {
                    'desktop-commander': {
                        'requests_per_minute': 600,
                        'queue_depth': 150,
                        'success_rate': 0.98
                    }
                }
            }
    
    scaler = MCPAutoScaler(MockMetrics())
    
    # Start monitoring
    await scaler.monitor_and_scale()

if __name__ == "__main__":
    asyncio.run(main())
