"""
Message methods for RubPlus
"""

from typing import Optional, Dict, Any
import httpx


class MessageMethods:
    """Methods for sending and managing messages"""
    
    def __init__(self, client: httpx.AsyncClient, base_url: str):
        self.client = client
        self.base_url = base_url
    
    async def send(
        self,
        chat_id: str,
        text: str,
        reply_to: Optional[str] = None,
        keyboard: Optional[Dict] = None,
        auto_delete: Optional[int] = None,
        parse_mode: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Send message"""
        data = {
            "chat_id": chat_id,
            "text": text
        }
        
        if reply_to:
            data["reply_to_message_id"] = reply_to
        if keyboard:
            data["chat_keypad"] = keyboard
            data["chat_keypad_type"] = "New"
        if metadata:
            data["metadata"] = metadata
        
        return await self._post("sendMessage", data)
    
    async def edit(
        self,
        chat_id: str,
        message_id: str,
        text: str,
        parse_mode: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Edit message"""
        data = {
            "chat_id": chat_id,
            "message_id": message_id,
            "text": text
        }
        
        if metadata:
            data["metadata"] = metadata
        
        return await self._post("editMessageText", data)
    
    async def delete(self, chat_id: str, message_id: str) -> Dict[str, Any]:
        """Delete message"""
        return await self._post("deleteMessage", {
            "chat_id": chat_id,
            "message_id": message_id
        })
    
    async def forward(
        self,
        from_chat_id: str,
        to_chat_id: str,
        message_id: str
    ) -> Dict[str, Any]:
        """Forward message"""
        return await self._post("forwardMessage", {
            "from_chat_id": from_chat_id,
            "to_chat_id": to_chat_id,
            "message_id": message_id
        })
    
    async def _post(self, method: str, data: Dict) -> Dict[str, Any]:
        """Post to API"""
        url = f"{self.base_url}/{method}"
        try:
            response = await self.client.post(url, json=data)
            return response.json()
        except Exception as e:
            return {"status": "ERROR", "error": str(e)}
