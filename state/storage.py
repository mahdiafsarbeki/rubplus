"""
Base Storage class for state management
"""

from abc import ABC, abstractmethod
from typing import Any, Optional, Dict


class Storage(ABC):
    """
    Abstract base class for state storage
    Implementations: MemoryStorage, RedisStorage, DatabaseStorage, etc.
    """
    
    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """Get value from storage"""
        pass
    
    @abstractmethod
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in storage with optional TTL (seconds)"""
        pass
    
    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Delete value from storage"""
        pass
    
    @abstractmethod
    async def exists(self, key: str) -> bool:
        """Check if key exists"""
        pass
    
    @abstractmethod
    async def get_all(self, pattern: str = "*") -> Dict[str, Any]:
        """Get all values matching pattern"""
        pass
    
    @abstractmethod
    async def clear(self) -> bool:
        """Clear all storage"""
        pass
