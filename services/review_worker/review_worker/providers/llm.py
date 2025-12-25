from typing import Dict, Type

from langchain_openai import ChatOpenAI
from review_worker.config import Settings
from review_worker.interfaces import LLMStrategy

_LLM_REGISTRY: Dict[str, Type[LLMStrategy]] = {}

def register_llm_strategy(name: str):
    """Decorator to register an LLM strategy."""
    def decorator(cls):
        _LLM_REGISTRY[name] = cls
        return cls
    return decorator

@register_llm_strategy("openai")
class OpenAIStrategy(LLMStrategy):
    def create_llm(self, settings: Settings) -> ChatOpenAI:
        return ChatOpenAI(
            api_key=lambda: settings.LLM_API_KEY,
            model=settings.LLM_MODEL_NAME,
            temperature=settings.LLM_TEMPERATURE
        )

@register_llm_strategy("local")
class LocalStrategy(LLMStrategy):
    def create_llm(self, settings: Settings) -> ChatOpenAI:
        return ChatOpenAI(
            base_url=settings.LLM_BASE_URL,
            api_key=lambda: "type-anything",
            model=settings.LLM_MODEL_NAME,
            temperature=settings.LLM_TEMPERATURE
        )

class LLMFactory:
    """
    Factory to retrieve LLM strategies.
    Decoupled from concrete implementations via the _LLM_REGISTRY.
    """
    @staticmethod
    def get_llm(settings: Settings) -> ChatOpenAI:
        provider = settings.LLM_MODEL_PROVIDER.lower()
        
        strategy_cls = _LLM_REGISTRY.get(provider)
        if not strategy_cls:
            raise ValueError(f"Unknown LLM Provider: {provider}. Available: {list(_LLM_REGISTRY.keys())}")
            
        # Instantiate and use the strategy
        strategy = strategy_cls()
        return strategy.create_llm(settings)