"""
Security Configuration for MCP Production
Implements defense-in-depth security measures
"""
import os
import jwt
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import asyncio
from functools import wraps
import logging

logger = logging.getLogger(__name__)

class SecurityManager:
    """Comprehensive security manager for MCP tools"""
    
    def __init__(self):
        self.jwt_secret = os.environ.get('JWT_SECRET', secrets.token_urlsafe(32))
        self.api_keys = self._load_api_keys()
        self.rate_limiter = RateLimiter()
        self.audit_logger = AuditLogger()
        
    def _load_api_keys(self) -> Dict[str, Dict[str, Any]]:
        """Load authorized API keys from secure storage"""
        # In production, load from secure vault
        return {
            os.environ.get('MCP_API_KEY', ''): {
                'name': 'default',
                'permissions': ['*'],
                'rate_limit': 1000
            }
        }
        
    async def authenticate(self, request) -> Optional[Dict[str, Any]]:
        """Authenticate request using API key or JWT"""
        
        # Check API key
        api_key = request.headers.get('Authorization', '').replace('Bearer ', '')
        if api_key in self.api_keys:
            user_info = self.api_keys[api_key]
            await self.audit_logger.log('auth.success', {'method': 'api_key', 'user': user_info['name']})
            return user_info
            
        # Check JWT token
        try:
            token_data = jwt.decode(api_key, self.jwt_secret, algorithms=['HS256'])
            await self.audit_logger.log('auth.success', {'method': 'jwt', 'user': token_data.get('sub')})
            return token_data
        except jwt.InvalidTokenError:
            pass
            
        await self.audit_logger.log('auth.failure', {'reason': 'invalid_credentials'})
        return None
        
    async def authorize(self, user_info: Dict[str, Any], resource: str, action: str) -> bool:
        """Check if user is authorized for specific action"""
        
        permissions = user_info.get('permissions', [])
        
        # Check wildcard permission
        if '*' in permissions:
            return True
            
        # Check specific permission
        required_permission = f"{resource}:{action}"
        if required_permission in permissions:
            return True
            
        # Check resource wildcard
        if f"{resource}:*" in permissions:
            return True
            
        await self.audit_logger.log('auth.denied', {
            'user': user_info.get('name'),
            'resource': resource,
            'action': action
        })
        
        return False
        
    def generate_token(self, user_id: str, permissions: List[str], 
                      expires_in: int = 3600) -> str:
        """Generate JWT token for user"""
        
        payload = {
            'sub': user_id,
            'permissions': permissions,
            'exp': datetime.utcnow() + timedelta(seconds=expires_in),
            'iat': datetime.utcnow()
        }
        
        return jwt.encode(payload, self.jwt_secret, algorithm='HS256')

class RateLimiter:
    """Token bucket rate limiter"""
    
    def __init__(self):
        self.buckets = {}
        self.default_rate = 100  # requests per minute
        self.default_burst = 10  # burst capacity
        
    async def check_rate_limit(self, user_id: str, rate: int = None) -> bool:
        """Check if request is within rate limit"""
        
        rate = rate or self.default_rate
        now = asyncio.get_event_loop().time()
        
        if user_id not in self.buckets:
            self.buckets[user_id] = {
                'tokens': self.default_burst,
                'last_update': now
            }
            
        bucket = self.buckets[user_id]
        
        # Refill tokens
        time_passed = now - bucket['last_update']
        tokens_to_add = time_passed * (rate / 60)  # Convert to per second
        bucket['tokens'] = min(self.default_burst, bucket['tokens'] + tokens_to_add)
        bucket['last_update'] = now
        
        # Check if request allowed
        if bucket['tokens'] >= 1:
            bucket['tokens'] -= 1
            return True
            
        return False
        
    def get_retry_after(self, user_id: str) -> int:
        """Get seconds until next request allowed"""
        
        if user_id not in self.buckets:
            return 0
            
        bucket = self.buckets[user_id]
        if bucket['tokens'] >= 1:
            return 0
            
        # Calculate time until 1 token available
        tokens_needed = 1 - bucket['tokens']
        seconds_needed = tokens_needed / (self.default_rate / 60)
        
        return int(seconds_needed) + 1

class InputValidator:
    """Validate and sanitize user inputs"""
    
    @staticmethod
    def validate_path(path: str, base_dir: str = "/workspace") -> str:
        """Validate and normalize file paths to prevent traversal"""
        
        # Normalize path
        normalized = os.path.normpath(path)
        
        # Convert to absolute path
        if not os.path.isabs(normalized):
            normalized = os.path.join(base_dir, normalized)
            
        # Ensure path is within base directory
        try:
            relative = os.path.relpath(normalized, base_dir)
            if relative.startswith('..'):
                raise ValueError("Path traversal attempt detected")
        except ValueError:
            raise ValueError(f"Invalid path: {path}")
            
        return normalized
        
    @staticmethod
    def validate_command(command: str, blocked_commands: List[str] = None) -> str:
        """Validate shell commands to prevent injection"""
        
        blocked_commands = blocked_commands or [
            'rm -rf', 'dd', 'mkfs', 'format', 
            ':(){:|:&};:', 'python -c', 'eval'
        ]
        
        # Check for blocked commands
        for blocked in blocked_commands:
            if blocked in command:
                raise ValueError(f"Blocked command pattern: {blocked}")
                
        # Check for suspicious patterns
        suspicious_patterns = [
            '&&', '||', ';', '`', '$(',  # Command chaining
            '>', '>>', '<', '|',          # Redirections
            '\\x', '\\n', '\\r'           # Escape sequences
        ]
        
        for pattern in suspicious_patterns:
            if pattern in command:
                logger.warning(f"Suspicious pattern in command: {pattern}")
                
        return command
        
    @staticmethod
    def sanitize_json(data: Dict[str, Any], max_depth: int = 10) -> Dict[str, Any]:
        """Sanitize JSON data to prevent injection attacks"""
        
        def _sanitize(obj, depth=0):
            if depth > max_depth:
                raise ValueError("JSON nesting too deep")
                
            if isinstance(obj, dict):
                return {k: _sanitize(v, depth + 1) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [_sanitize(item, depth + 1) for item in obj]
            elif isinstance(obj, str):
                # Remove null bytes and control characters
                return ''.join(char for char in obj if ord(char) >= 32)
            else:
                return obj
                
        return _sanitize(data)

class AuditLogger:
    """Security audit logging"""
    
    def __init__(self):
        self.logger = logging.getLogger('security.audit')
        self.logger.setLevel(logging.INFO)
        
    async def log(self, event_type: str, details: Dict[str, Any]):
        """Log security event"""
        
        event = {
            'timestamp': datetime.utcnow().isoformat(),
            'event_type': event_type,
            'details': details,
            'request_id': details.get('request_id'),
            'user': details.get('user'),
            'ip_address': details.get('ip_address')
        }
        
        self.logger.info(json.dumps(event))
        
        # For critical events, also send to monitoring
        if event_type in ['auth.failure', 'auth.denied', 'security.violation']:
            await self._alert_security_team(event)
            
    async def _alert_security_team(self, event: Dict[str, Any]):
        """Send alert for critical security events"""
        # Implementation depends on alerting system
        pass

class EncryptionManager:
    """Handle encryption for sensitive data"""
    
    def __init__(self):
        self.key = os.environ.get('ENCRYPTION_KEY', '').encode()
        if not self.key:
            self.key = secrets.token_bytes(32)
            
    def encrypt_sensitive_field(self, data: str) -> str:
        """Encrypt sensitive data fields"""
        # Use Fernet or similar for production
        # This is a simplified example
        import base64
        from cryptography.fernet import Fernet
        
        f = Fernet(base64.urlsafe_b64encode(self.key[:32]))
        return f.encrypt(data.encode()).decode()
        
    def decrypt_sensitive_field(self, encrypted: str) -> str:
        """Decrypt sensitive data fields"""
        import base64
        from cryptography.fernet import Fernet
        
        f = Fernet(base64.urlsafe_b64encode(self.key[:32]))
        return f.decrypt(encrypted.encode()).decode()

# Security decorators for FastAPI/Flask routes
def require_auth(permissions: List[str] = None):
    """Decorator to require authentication"""
    def decorator(func):
        @wraps(func)
        async def wrapper(request, *args, **kwargs):
            security = SecurityManager()
            
            user_info = await security.authenticate(request)
            if not user_info:
                return {'error': 'Unauthorized'}, 401
                
            # Check rate limit
            if not await security.rate_limiter.check_rate_limit(user_info.get('name')):
                retry_after = security.rate_limiter.get_retry_after(user_info.get('name'))
                return {
                    'error': 'Rate limit exceeded',
                    'retry_after': retry_after
                }, 429
                
            # Check permissions if specified
            if permissions:
                for permission in permissions:
                    resource, action = permission.split(':')
                    if not await security.authorize(user_info, resource, action):
                        return {'error': 'Forbidden'}, 403
                        
            # Add user info to request
            request.user_info = user_info
            
            return await func(request, *args, **kwargs)
        return wrapper
    return decorator

def validate_input(schema: Dict[str, Any]):
    """Decorator to validate request input"""
    def decorator(func):
        @wraps(func)
        async def wrapper(request, *args, **kwargs):
            validator = InputValidator()
            
            try:
                # Get request data
                data = await request.json()
                
                # Sanitize JSON
                data = validator.sanitize_json(data)
                
                # Validate paths if present
                if 'path' in data and 'path' in schema:
                    data['path'] = validator.validate_path(data['path'])
                    
                # Validate commands if present
                if 'command' in data and 'command' in schema:
                    data['command'] = validator.validate_command(data['command'])
                    
                request.validated_data = data
                
            except Exception as e:
                return {'error': f'Invalid input: {str(e)}'}, 400
                
            return await func(request, *args, **kwargs)
        return wrapper
    return decorator

# Example secure endpoint
@require_auth(['desktop:write'])
@validate_input({'path': str, 'content': str})
async def secure_file_write(request):
    """Example of secured file write endpoint"""
    
    data = request.validated_data
    user_info = request.user_info
    
    # Log the operation
    await AuditLogger().log('file.write', {
        'user': user_info.get('name'),
        'path': data['path'],
        'size': len(data['content'])
    })
    
    # Perform the operation
    # ... actual file write logic ...
    
    return {'success': True}

# Security headers middleware
class SecurityHeadersMiddleware:
    """Add security headers to all responses"""
    
    def __init__(self, app):
        self.app = app
        
    async def __call__(self, scope, receive, send):
        if scope['type'] == 'http':
            async def send_wrapper(message):
                if message['type'] == 'http.response.start':
                    headers = dict(message['headers'])
                    
                    # Add security headers
                    security_headers = [
                        (b'X-Content-Type-Options', b'nosniff'),
                        (b'X-Frame-Options', b'DENY'),
                        (b'X-XSS-Protection', b'1; mode=block'),
                        (b'Strict-Transport-Security', b'max-age=31536000; includeSubDomains'),
                        (b'Content-Security-Policy', b"default-src 'self'"),
                        (b'Referrer-Policy', b'strict-origin-when-cross-origin')
                    ]
                    
                    for header, value in security_headers:
                        headers[header] = value
                        
                    message['headers'] = list(headers.items())
                    
                await send(message)
                
            await self.app(scope, receive, send_wrapper)
        else:
            await self.app(scope, receive, send)

if __name__ == "__main__":
    # Example usage
    security = SecurityManager()
    
    # Generate token
    token = security.generate_token('user123', ['desktop:read', 'github:*'])
    print(f"Generated token: {token}")
    
    # Test rate limiter
    limiter = RateLimiter()
    for i in range(15):
        allowed = asyncio.run(limiter.check_rate_limit('user123'))
        print(f"Request {i+1}: {'Allowed' if allowed else 'Blocked'}")
