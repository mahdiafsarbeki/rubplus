"""
Decorators for event handling
"""

from typing import Callable, Optional, List, Any
from functools import wraps
import inspect


class HandlerDecorator:
    """
    Decorator system for event handlers
    """
    
    def __init__(self):
        self.handlers = {}
    
    def on_message(self, filters=None, commands: Optional[List[str]] = None):
        """Decorator for message handlers"""
        def decorator(func: Callable) -> Callable:
            handler_key = "message"
            if not handler_key in self.handlers:
                self.handlers[handler_key] = []
            
            self.handlers[handler_key].append({
                'func': func,
                'filters': filters,
                'commands': commands
            })
            return func
        return decorator
    
    def on_edited_message(self, filters=None):
        """Decorator for edited message handlers"""
        def decorator(func: Callable) -> Callable:
            handler_key = "edited_message"
            if handler_key not in self.handlers:
                self.handlers[handler_key] = []
            
            self.handlers[handler_key].append({
                'func': func,
                'filters': filters
            })
            return func
        return decorator
    
    def on_callback(self, callback_id: Optional[str] = None):
        """Decorator for callback query handlers"""
        def decorator(func: Callable) -> Callable:
            handler_key = f"callback:{callback_id}" if callback_id else "callback"
            if handler_key not in self.handlers:
                self.handlers[handler_key] = []
            
            self.handlers[handler_key].append({
                'func': func,
                'callback_id': callback_id
            })
            return func
        return decorator
    
    def on_command(self, command: str):
        """Decorator for command handlers"""
        def decorator(func: Callable) -> Callable:
            handler_key = f"command:{command}"
            if handler_key not in self.handlers:
                self.handlers[handler_key] = []
            
            self.handlers[handler_key].append({
                'func': func,
                'command': command
            })
            return func
        return decorator
    
    def on_user_joined(self):
        """Decorator for user joined handlers"""
        def decorator(func: Callable) -> Callable:
            handler_key = "user_joined"
            if handler_key not in self.handlers:
                self.handlers[handler_key] = []
            
            self.handlers[handler_key].append({'func': func})
            return func
        return decorator
    
    def on_user_left(self):
        """Decorator for user left handlers"""
        def decorator(func: Callable) -> Callable:
            handler_key = "user_left"
            if handler_key not in self.handlers:
                self.handlers[handler_key] = []
            
            self.handlers[handler_key].append({'func': func})
            return func
        return decorator
    
    def on_error(self):
        """Decorator for error handlers"""
        def decorator(func: Callable) -> Callable:
            self.handlers['error'] = {'func': func}
            return func
        return decorator
    
    def get_handlers(self, event_type: str) -> List[dict]:
        """Get all handlers for specific event type"""
        handlers = []
        
        # Check exact match
        if event_type in self.handlers:
            handlers.append(self.handlers[event_type])
        
        # Check pattern matches
        for key, handler in self.handlers.items():
            if key.startswith(event_type + ":"):
                handlers.append(handler)
        
        return handlers if isinstance(handlers[0], list) and handlers else (handlers if handlers else [])
