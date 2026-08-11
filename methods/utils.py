"""
Utility methods for RubPlus
"""

from typing import Dict, Any


class UtilityMethods:
    """Utility methods"""
    
    def __init__(self, client, base_url: str):\n        self.client = client\n        self.base_url = base_url\n    \n    async def get_me(self) -> Dict[str, Any]:\n        \"\"\"Get bot info\"\"\"\n        return await self._post(\"getMe\", {})\n    \n    async def set_commands(self, commands: list) -> Dict[str, Any]:\n        \"\"\"Set bot commands\"\"\"\n        return await self._post(\"setCommands\", {\n            \"bot_commands\": commands\n        })\n    \n    async def _post(self, method: str, data: Dict) -> Dict[str, Any]:\n        url = f\"{self.base_url}/{method}\"\n        try:\n            response = await self.client.post(url, json=data)\n            return response.json()\n        except Exception as e:\n            return {\"status\": \"ERROR\", \"error\": str(e)}\n