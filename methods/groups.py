"""
Group management methods
"""

from typing import Optional, Dict, Any


class GroupMethods:
    """Methods for group management"""
    
    def __init__(self, client, base_url: str):
        self.client = client
        self.base_url = base_url
    
    async def ban_member(self, chat_id: str, user_id: str) -> Dict[str, Any]:
        """Ban user from group"""
        return await self._post("banChatMember", {
            "chat_id": chat_id,
            "user_id": user_id
        })
    
    async def unban_member(self, chat_id: str, user_id: str) -> Dict[str, Any]:
        """Unban user from group"""
        return await self._post("unbanChatMember", {
            "chat_id": chat_id,
            "user_id": user_id
        })
    
    async def promote_member(
        self,
        chat_id: str,
        user_id: str,
        is_admin: bool = True
    ) -> Dict[str, Any]:
        """Promote/demote user"""
        return await self._post("promoteChatMember", {
            "chat_id": chat_id,
            "user_id": user_id,
            "is_admin": is_admin
        })
    
    async def change_title(self, chat_id: str, title: str) -> Dict[str, Any]:
        """Change group title"""
        return await self._post("editChatTitle", {
            "chat_id": chat_id,
            "title": title
        })
    
    async def change_description(
        self,
        chat_id: str,
        description: str
    ) -> Dict[str, Any]:
        """Change group description"""
        return await self._post("editChatDescription", {
            "chat_id": chat_id,
            "description": description
        })
    
    async def pin_message(self, chat_id: str, message_id: str) -> Dict[str, Any]:
        """Pin message in group"""
        return await self._post("pinMessage", {
            "chat_id": chat_id,
            "message_id": message_id
        })
    
    async def unpin_message(self, chat_id: str, message_id: str) -> Dict[str, Any]:
        """Unpin message from group"""
        return await self._post("unpinMessage", {
            "chat_id": chat_id,
            "message_id": message_id
        })
    
    async def leave(self, chat_id: str) -> Dict[str, Any]:
        """Leave group"""
        return await self._post("leaveChat", {"chat_id": chat_id})
    
    async def get_info(self, chat_id: str) -> Dict[str, Any]:
        """Get group info"""
        return await self._post("getChat", {"chat_id": chat_id})
    
    async def _post(self, method: str, data: Dict) -> Dict[str, Any]:
        url = f"{self.base_url}/{method}"
        try:
            response = await self.client.post(url, json=data)
            return response.json()
        except Exception as e:
            return {"status": "ERROR", "error": str(e)}
