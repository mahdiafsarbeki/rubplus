"""
RubPlus Main Client - v2.0.0
Modern, Simple & Powerful Rubika Bot API
"""

import asyncio
import httpx
from typing import Optional, Callable, Dict, Any, List
from datetime import datetime

from config import Config
from types import Message, CallbackQuery, Update, User, Chat
from logger import RubPlusLogger, LogLevel
from filters import Filter, text, command, private
from keyboard import InlineKeyboard, ReplyKeyboard
from handlers.decorators import HandlerDecorator
from handlers.middleware import MiddlewareManager, RateLimitMiddleware, LoggingMiddleware
from handlers.error_handler import ErrorHandler, RubPlusException
from state.memory import MemoryStorage
from state.storage import UserState
from methods import MessageMethods
from methods.callbacks import CallbackMethods
from methods.groups import GroupMethods
from methods.utils import UtilityMethods


class RubPlus:
    """
    Main RubPlus Client
    Simple and powerful API for Rubika Bot
    """
    
    VERSION = "2.0.0"
    BASE_URL = "https://api.rubika.io/bot"
    
    def __init__(self, config: Config):
        """Initialize RubPlus client"""
        self.config = config
        config.validate()
        
        # Logger
        self.logger = RubPlusLogger(
            level=LogLevel[config.log_level.upper()],
            log_file=config.log_file,
            use_colors=True
        )
        
        # HTTP Client
        self.client = httpx.AsyncClient(
            timeout=config.timeout,
            headers={"Authorization": f"Bearer {config.token}"}
        )
        
        # State management
        self.storage = MemoryStorage()
        
        # Handlers
        self.handlers = HandlerDecorator()
        self.error_handler = ErrorHandler(self.logger)
        
        # Middleware
        self.middleware = MiddlewareManager()
        self.middleware.add(RateLimitMiddleware(max_requests=50))
        self.middleware.add(LoggingMiddleware(self.logger))
        
        # API Methods
        self.messages = MessageMethods(self.client, self.BASE_URL)
        self.callbacks = CallbackMethods(self.client, self.BASE_URL)
        self.groups = GroupMethods(self.client, self.BASE_URL)
        self.utils = UtilityMethods(self.client, self.BASE_URL)
        
        # State
        self._is_running = False
        self._update_offset = 0
    
    async def start(self):
        """Start bot"""
        self.logger.startup(self.VERSION)
        self._is_running = True
        
        try:
            # Connect and verify token
            bot_info = await self.utils.get_me()
            if bot_info.get("status") == "OK":
                self.logger.connected()
            else:
                raise RubPlusException("Failed to connect - Invalid token")
            
            # Start update loop
            await self.logger.success()
            await self._update_loop()
            
        except Exception as e:
            self.logger.error(f"Failed to start: {str(e)}")
            raise
    
    async def _update_loop(self):
        """Main update loop"""
        polling_limit = self.config.polling_limit
        
        while self._is_running:
            try:
                # Get updates
                updates = await self._get_updates(
                    offset=self._update_offset,
                    limit=polling_limit
                )
                
                if not updates:
                    await asyncio.sleep(0.5)
                    continue
                
                # Process updates
                for update in updates:
                    asyncio.create_task(self._process_update(update))
                    self._update_offset = update.get("update_id", 0) + 1
                
            except Exception as e:
                await self.error_handler.handle(e)
                await asyncio.sleep(1)
    
    async def _get_updates(self, offset: int = 0, limit: int = 50) -> List[Dict]:
        """Get updates from server"""
        try:
            response = await self.client.post(
                f"{self.BASE_URL}/getUpdates",
                json={"offset": offset, "limit": limit}
            )
            data = response.json()
            return data.get("result", []) if data.get("status") == "OK" else []
        except Exception as e:
            self.logger.error(f"Failed to get updates: {str(e)}")
            return []
    
    async def _process_update(self, raw_update: Dict[str, Any]):
        """Process single update"""
        try:
            # Check update type
            if "message" in raw_update:
                message = Message.from_dict(raw_update["message"], bot=self)
                
                # Apply middleware
                message = await self.middleware.process(message)
                if not message:
                    return
                
                # Call handlers
                await self._call_message_handlers(message)
            
            elif "callback_query" in raw_update:
                callback = CallbackQuery.from_dict(raw_update["callback_query"], bot=self)
                
                # Apply middleware
                callback = await self.middleware.process(callback)
                if not callback:
                    return
                
                # Call handlers
                await self._call_callback_handlers(callback)
        
        except Exception as e:
            await self.error_handler.handle(e, raw_update)
    
    async def _call_message_handlers(self, message: Message):
        """Call message handlers"""
        handlers = self.handlers.get_handlers("message")
        
        for handler_info in handlers:
            try:
                # Check filters
                if handler_info.get("filters"):
                    if not handler_info["filters"](message.raw_data):
                        continue
                
                # Call handler
                func = handler_info["func"]
                if asyncio.iscoroutinefunction(func):
                    await func(message)
                else:
                    func(message)
            
            except Exception as e:
                await self.error_handler.handle(e, message)
    
    async def _call_callback_handlers(self, callback: CallbackQuery):
        """Call callback handlers"""
        handlers = self.handlers.get_handlers(f"callback:{callback.data}")
        
        if not handlers:
            handlers = self.handlers.get_handlers("callback")
        
        for handler_info in handlers:
            try:
                func = handler_info["func"]
                if asyncio.iscoroutinefunction(func):
                    await func(callback)
                else:
                    func(callback)
            
            except Exception as e:
                await self.error_handler.handle(e, callback)
    
    # Decorators
    def on_message(self, filters: Optional[Filter] = None):
        """Decorator for message handlers"""
        return self.handlers.on_message(filters)
    
    def on_command(self, cmd: str):
        """Decorator for command handlers"""
        return self.handlers.on_command(cmd)
    
    def on_callback(self, callback_id: Optional[str] = None):
        """Decorator for callback handlers"""
        return self.handlers.on_callback(callback_id)
    
    def on_error(self, error_type: type = Exception):
        """Decorator for error handlers"""
        return self.error_handler.on_error(error_type)
    
    # Shortcuts
    async def send(
        self,
        chat_id: str,
        text: str,
        keyboard: Optional[Dict] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Send message shortcut"""
        return await self.messages.send(chat_id, text, keyboard=keyboard, **kwargs)
    
    def get_user_state(self, user_id: str) -> UserState:
        """Get user state storage"""
        return UserState(user_id, self.storage)
    
    async def stop(self):
        """Stop bot"""
        self._is_running = False
        await self.client.aclose()
        self.logger.info("Bot stopped")
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.stop()


# Convenience function
async def create_bot(token: str, **kwargs) -> RubPlus:
    """Create and return RubPlus bot instance"""
    config = Config(token=token, **kwargs)
    return RubPlus(config)
