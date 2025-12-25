from abc import ABC, abstractmethod
from typing import Any
from shared.config import Settings

class RedisStrategy(ABC):
    @abstractmethod
    def create_client(self, settings: Settings, **kwargs) -> Any:
        """
        Creates and returns a Redis client (async).
        Accepts **kwargs for specific connection options (e.g., max_connections).
        """
        pass