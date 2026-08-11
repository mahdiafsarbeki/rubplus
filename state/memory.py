"""
In-Memory Storage Implementation
"""

import asyncio
import time
import re
from typing import Any, Optional, Dict
from .storage import Storage


class MemoryStorage(Storage):
    """
    Simple in-memory storage for state management
    """
    
    def __init__(self):
        self._data: Dict[str, Any] = {}
        self._ttl: Dict[str, float] = {}
    
    async def get(self, key: str) -> Optional[Any]:
        if key not in self._data:
            return None
        
        if key in self._ttl:
            if time.time() > self._ttl[key]:
                await self.delete(key)
                return None
        
        return self._data.get(key)
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        self._data[key] = value
        
        if ttl:
            self._ttl[key] = time.time() + ttl
        elif key in self._ttl:
            del self._ttl[key]
        
        return True
    
    async def delete(self, key: str) -> bool:
        if key in self._data:
            del self._data[key]
        if key in self._ttl:
            del self._ttl[key]
        return True
    
    async def exists(self, key: str) -> bool:
        return key in self._data
    
    async def get_all(self, pattern: str = "*") -> Dict[str, Any]:
        if pattern == "*":
            return dict(self._data)
        
        regex_pattern = pattern.replace("*", ".*")
        return {
            k: v for k, v in self._data.items()
            if re.match(regex_pattern, k)
        }
    
    async def clear(self) -> bool:
        self._data.clear()
        self._ttl.clear()
        return True
