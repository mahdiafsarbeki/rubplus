"""
Error handling system for RubPlus
"""

from typing import Callable, Optional, Any, Type
from abc import ABC


class ErrorHandler:
    """
    Error handling manager
    """
    
    def __init__(self, logger):
        self.logger = logger
        self.error_handlers = {}
    
    def register(self, error_type: Type[Exception], handler: Callable):
        """Register handler for specific error type"""
        self.error_handlers[error_type] = handler
    
    async def handle(self, error: Exception, update: Any = None):
        """Handle error"""
        error_type = type(error)
        
        # Log error
        self.logger.error(str(error))
        
        # Call registered handler if exists
        if error_type in self.error_handlers:
            handler = self.error_handlers[error_type]
            try:
                await handler(error, update)
            except Exception as e:
                self.logger.error(f"Error in error handler: {str(e)}")
        
        # Call generic error handler
        if Exception in self.error_handlers:
            handler = self.error_handlers[Exception]
            try:
                await handler(error, update)
            except Exception as e:
                self.logger.error(f"Error in generic error handler: {str(e)}")
    
    def on_error(self, error_type: Type[Exception] = Exception):
        """Decorator for error handlers"""
        def decorator(func: Callable) -> Callable:
            self.register(error_type, func)
            return func
        return decorator


class RubPlusException(Exception):
    """Base exception for RubPlus"""
    pass


class APIError(RubPlusException):
    """API error"""
    def __init__(self, message: str, status: str = None):
        self.message = message
        self.status = status
        super().__init__(message)


class InvalidTokenError(RubPlusException):
    """Invalid token error"""
    pass


class ConnectionError(RubPlusException):
    """Connection error"""
    pass


class TimeoutError(RubPlusException):
    """Timeout error"""
    pass
