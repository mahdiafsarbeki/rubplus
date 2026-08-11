"""
RubPlus Type Definitions and Data Classes
Version 2.0.0
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from datetime import datetime


@dataclass
class User:
    """User object"""
    id: str
    first_name: str
    last_name: Optional[str] = None
    username: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
        return cls(
            id=data.get('id'),
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            username=data.get('username')
        )
    
    def full_name(self) -> str:
        """Get full name of user"""
        name = self.first_name or ""
        if self.last_name:
            name += f" {self.last_name}"
        return name.strip()


@dataclass
class Chat:
    """Chat object (private or group)"""
    id: str
    title: Optional[str] = None
    is_private: bool = True
    is_group: bool = False
    members_count: Optional[int] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Chat':
        return cls(
            id=data.get('id'),
            title=data.get('title'),
            is_private=data.get('id', '').startswith('b0'),
            is_group=data.get('id', '').startswith('g0'),
            members_count=data.get('members_count')
        )
    
    def is_pm(self) -> bool:
        """Check if chat is private message"""
        return self.is_private


@dataclass
class File:
    """File attachment"""
    file_id: str
    file_name: str
    file_size: int
    mime_type: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'File':
        return cls(
            file_id=data.get('file_id'),
            file_name=data.get('file_name'),
            file_size=data.get('file_size'),
            mime_type=data.get('mime_type')
        )


@dataclass
class Message:
    """Message object with rich context"""
    message_id: str
    chat: Chat
    sender: User
    text: Optional[str] = None
    timestamp: int = field(default_factory=lambda: int(datetime.now().timestamp()))
    file: Optional[File] = None
    is_photo: bool = False
    is_video: bool = False
    is_audio: bool = False
    is_document: bool = False
    reply_to_message_id: Optional[str] = None
    raw_data: Dict[str, Any] = field(default_factory=dict)
    
    # Callbacks for reply and other operations
    _reply_func: Optional[Any] = field(default=None, repr=False)
    _bot: Optional[Any] = field(default=None, repr=False)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], bot=None) -> 'Message':
        """Create Message from raw API data"""
        chat = Chat.from_dict({'id': data.get('chat_id')})
        sender = User.from_dict(data.get('sender', {}))
        file_data = data.get('file')
        file = File.from_dict(file_data) if file_data else None
        
        msg = cls(
            message_id=data.get('message_id'),
            chat=chat,
            sender=sender,
            text=data.get('text'),
            timestamp=int(data.get('time', 0)),
            file=file,
            is_photo=data.get('photo', False),
            is_video=data.get('video', False),
            is_audio=data.get('audio', False),
            is_document=data.get('document', False),
            reply_to_message_id=data.get('reply_to_message_id'),
            raw_data=data,
            _bot=bot
        )
        return msg
    
    async def reply(self, text: str, parse_mode: Optional[str] = None, keyboard=None, auto_delete: Optional[int] = None):
        """Reply to this message"""
        if not self._bot:
            raise RuntimeError("Bot instance not attached to message")
        return await self._bot.send(
            self.chat.id,
            text,
            reply_to=self.message_id,
            parse_mode=parse_mode,
            keyboard=keyboard,
            auto_delete=auto_delete
        )
    
    async def edit(self, text: str, parse_mode: Optional[str] = None):
        """Edit this message"""
        if not self._bot:
            raise RuntimeError("Bot instance not attached to message")
        return await self._bot.edit(self.chat.id, self.message_id, text, parse_mode)
    
    async def delete(self):
        """Delete this message"""
        if not self._bot:
            raise RuntimeError("Bot instance not attached to message")
        return await self._bot.delete(self.chat.id, self.message_id)
    
    async def forward(self, to_chat_id: str):
        """Forward this message to another chat"""
        if not self._bot:
            raise RuntimeError("Bot instance not attached to message")
        return await self._bot.forward(self.chat.id, to_chat_id, self.message_id)


@dataclass
class CallbackQuery:
    """Callback query from inline button"""
    callback_id: str
    message: Message
    data: str
    
    _bot: Optional[Any] = field(default=None, repr=False)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], bot=None) -> 'CallbackQuery':
        """Create CallbackQuery from raw API data"""
        message = Message.from_dict(data.get('message', {}), bot)
        return cls(
            callback_id=data.get('callback_id'),
            message=message,
            data=data.get('data'),
            _bot=bot
        )
    
    async def answer(self, text: str = None, alert: bool = False):
        """Answer the callback query with a notification"""
        if not self._bot:
            raise RuntimeError("Bot instance not attached to callback")
        # Implementation in methods/callbacks.py
        pass
    
    async def edit_message(self, text: str, parse_mode: Optional[str] = None):
        """Edit the message associated with this callback"""
        if not self._bot:
            raise RuntimeError("Bot instance not attached to callback")
        return await self.message.edit(text, parse_mode)


@dataclass
class Update:
    """Generic update object"""
    update_id: str
    update_type: str  # NewMessage, EditedMessage, CallbackQuery, etc.
    data: Dict[str, Any]
    timestamp: int = field(default_factory=lambda: int(datetime.now().timestamp()))
