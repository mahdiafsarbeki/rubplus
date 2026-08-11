"""
Type definitions for RubPlus v2.0.0
"""

from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class User:
    """User information"""
    id: str
    first_name: str
    last_name: Optional[str] = None
    username: Optional[str] = None
    avatar: Optional[str] = None
    bio: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
        return cls(
            id=data.get("user_id", ""),
            first_name=data.get("first_name", ""),
            last_name=data.get("last_name"),
            username=data.get("username"),
            avatar=data.get("avatar"),
            bio=data.get("bio")
        )
    
    @property
    def full_name(self) -> str:
        """Get full name"""
        if self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.first_name
    
    @property
    def mention(self) -> str:
        """Get mention string"""
        if self.username:
            return f"@{self.username}"
        return self.full_name


@dataclass
class Chat:
    """Chat information"""
    id: str
    title: Optional[str] = None
    is_group: bool = False
    members_count: int = 0
    description: Optional[str] = None
    avatar: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Chat':
        chat_id = data.get("chat_id", "")
        return cls(
            id=chat_id,
            title=data.get("title"),
            is_group=chat_id.startswith("g0"),
            members_count=data.get("members_count", 0),
            description=data.get("description"),
            avatar=data.get("avatar")
        )


@dataclass
class Message:
    """Message object"""
    message_id: str
    chat_id: str
    text: Optional[str] = None
    sender: Optional[User] = None
    reply_to_message_id: Optional[str] = None
    is_edited: bool = False
    created_at: Optional[datetime] = None
    raw_data: Dict[str, Any] = field(default_factory=dict)
    bot: Optional[Any] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], bot=None) -> 'Message':
        sender_data = data.get("from", {})
        return cls(
            message_id=data.get("message_id", ""),
            chat_id=data.get("chat_id", ""),
            text=data.get("text"),
            sender=User.from_dict(sender_data) if sender_data else None,
            reply_to_message_id=data.get("reply_to_message_id"),
            is_edited=data.get("is_edited", False),
            created_at=datetime.fromtimestamp(data.get("date", 0)) if data.get("date") else None,
            raw_data=data,
            bot=bot
        )
    
    async def reply(self, text: str, **kwargs):
        """Reply to message"""
        if self.bot:
            return await self.bot.send(
                self.chat_id,
                text,
                reply_to=self.message_id,
                **kwargs
            )
    
    async def edit(self, text: str, **kwargs):
        """Edit message"""
        if self.bot:
            return await self.bot.messages.edit(
                self.chat_id,
                self.message_id,
                text,
                **kwargs
            )
    
    async def delete(self):
        """Delete message"""
        if self.bot:
            return await self.bot.messages.delete(
                self.chat_id,
                self.message_id
            )


@dataclass
class CallbackQuery:
    """Callback query object"""
    callback_id: str
    user: Optional[User] = None
    chat_id: Optional[str] = None
    message_id: Optional[str] = None
    data: Optional[str] = None
    raw_data: Dict[str, Any] = field(default_factory=dict)
    bot: Optional[Any] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], bot=None) -> 'CallbackQuery':
        from_data = data.get("from", {})
        return cls(
            callback_id=data.get("id", ""),
            user=User.from_dict(from_data) if from_data else None,
            chat_id=data.get("chat_id"),
            message_id=data.get("message_id"),
            data=data.get("data"),
            raw_data=data,
            bot=bot
        )
    
    async def answer(self, text: Optional[str] = None, alert: bool = False):
        """Answer callback query"""
        if self.bot:
            return await self.bot.callbacks.answer(
                self.callback_id,
                text=text,
                alert=alert
            )


@dataclass
class Update:
    """Update wrapper"""
    update_id: int
    message: Optional[Message] = None
    callback_query: Optional[CallbackQuery] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], bot=None) -> 'Update':
        return cls(
            update_id=data.get("update_id", 0),
            message=Message.from_dict(data["message"], bot=bot) if "message" in data else None,
            callback_query=CallbackQuery.from_dict(data["callback_query"], bot=bot) if "callback_query" in data else None
        )


class UserState:
    """User state storage wrapper"""
    
    def __init__(self, user_id: str, storage):
        self.user_id = user_id
        self.storage = storage
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """Set user state"""
        full_key = f"user:{self.user_id}:{key}"
        return await self.storage.set(full_key, value, ttl)
    
    async def get(self, key: str) -> Optional[Any]:
        """Get user state"""
        full_key = f"user:{self.user_id}:{key}"
        return await self.storage.get(full_key)
    
    async def delete(self, key: str):
        """Delete user state"""
        full_key = f"user:{self.user_id}:{key}"
        return await self.storage.delete(full_key)
    
    async def clear(self):
        """Clear all user state"""
        pattern = f"user:{self.user_id}:*"
        states = await self.storage.get_all(pattern)
        for key in states.keys():
            await self.storage.delete(key)
