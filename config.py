"""
RubPlus Configuration Management
Version 2.0.0
"""

import os
from typing import Optional
from enum import Enum


class LogLevel(Enum):
    """Log levels for RubPlus"""
    ERROR = 1
    WARNING = 2
    INFO = 3
    DEBUG = 4


class Config:
    """
    Configuration manager for RubPlus
    Supports environment variables and direct initialization
    """
    
    def __init__(
        self,
        token: str,
        debug: bool = False,
        skip_old_messages: bool = True,
        log_level: str = "info",
        log_file: Optional[str] = None,
        timeout: float = 60.0,
        polling_limit: int = 50,
        db_path: Optional[str] = None,
        webhook_secret: Optional[str] = None
    ):
        self.token = token
        self.debug = debug
        self.skip_old_messages = skip_old_messages
        self.log_level = log_level
        self.log_file = log_file
        self.timeout = timeout
        self.polling_limit = polling_limit
        self.db_path = db_path or "rubplus_data.db"
        self.webhook_secret = webhook_secret
    
    @classmethod
    def from_env(cls) -> 'Config':
        """
        Load configuration from environment variables
        
        Supported env vars:
        - RUBPLUS_TOKEN: Bot token (required)
        - RUBPLUS_DEBUG: Debug mode (true/false)
        - RUBPLUS_LOG_LEVEL: Log level (error, warning, info, debug)
        - RUBPLUS_LOG_FILE: Log file path
        - RUBPLUS_DB_PATH: Database file path
        - RUBPLUS_WEBHOOK_SECRET: Webhook secret token
        """
        token = os.getenv("RUBPLUS_TOKEN")
        if not token:
            raise ValueError("RUBPLUS_TOKEN environment variable is required")
        
        return cls(
            token=token,
            debug=os.getenv("RUBPLUS_DEBUG", "false").lower() == "true",
            log_level=os.getenv("RUBPLUS_LOG_LEVEL", "info"),
            log_file=os.getenv("RUBPLUS_LOG_FILE"),
            db_path=os.getenv("RUBPLUS_DB_PATH"),
            webhook_secret=os.getenv("RUBPLUS_WEBHOOK_SECRET")
        )
    
    def validate(self) -> bool:
        """Validate configuration"""
        if not self.token or len(self.token) < 10:
            raise ValueError("Invalid token")
        if self.timeout <= 0:
            raise ValueError("Timeout must be positive")
        if self.polling_limit <= 0 or self.polling_limit > 100:
            raise ValueError("Polling limit must be between 1 and 100")
        return True
