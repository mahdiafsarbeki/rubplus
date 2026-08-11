"""
Middleware system for RubPlus
"""

from typing import Callable, Optional, Any
from abc import ABC, abstractmethod


class Middleware(ABC):
    """
    Base class for middleware
    Middleware can intercept and modify updates before they reach handlers
    """
    
    @abstractmethod
    async def process(self, update: Any) -> Optional[Any]:
        """
        Process update
        Return None to skip this update
        Return modified update to pass to handlers
        """
        pass


class RateLimitMiddleware(Middleware):
    """Rate limiting middleware"""
    
    def __init__(self, max_requests: int = 30, time_window: int = 60):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = {}
    
    async def process(self, update: Any) -> Optional[Any]:
        import time
        
        user_id = update.raw_data.get('sender_id', 'unknown')
        current_time = time.time()
        
        if user_id not in self.requests:
            self.requests[user_id] = []
        
        # Remove old requests outside time window
        self.requests[user_id] = [
            req_time for req_time in self.requests[user_id]
            if current_time - req_time < self.time_window
        ]
        
        # Check rate limit
        if len(self.requests[user_id]) >= self.max_requests:
            return None  # Skip this update
        
        self.requests[user_id].append(current_time)
        return update


class LoggingMiddleware(Middleware):
    """Logging middleware"""
    
    def __init__(self, logger):
        self.logger = logger
    
    async def process(self, update: Any) -> Optional[Any]:
        self.logger.message_received(
            update.sender.id if hasattr(update, 'sender') else 'unknown',
            update.text if hasattr(update, 'text') else None
        )
        return update


class PermissionMiddleware(Middleware):
    """Permission checking middleware"""
    
    def __init__(self, admin_ids: list = None):
        self.admin_ids = admin_ids or []
    
    async def process(self, update: Any) -> Optional[Any]:
        # Add permission checking logic
        return update


class MiddlewareManager:
    """Manager for middleware"""
    
    def __init__(self):
        self.middlewares = []
    
    def add(self, middleware: Middleware):
        """Add middleware"""
        self.middlewares.append(middleware)
    
    def remove(self, middleware: Middleware):
        """Remove middleware"""
        self.middlewares.remove(middleware)
    
    async def process(self, update: Any) -> Optional[Any]:
        """Process update through all middleware"""
        for middleware in self.middlewares:
            update = await middleware.process(update)
            if update is None:
                return None
        return update
