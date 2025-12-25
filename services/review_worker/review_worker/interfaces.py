from abc import ABC, abstractmethod
from typing import Any
from review_worker.config import Settings

class LLMStrategy(ABC):
    @abstractmethod
    def create_llm(self, settings: Settings) -> Any:
        """
        Creates and returns a configured LLM object (e.g., ChatOpenAI).
        """
        pass