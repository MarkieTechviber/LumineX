from abc import ABC, abstractmethod
from typing import AsyncIterator, List, Dict, Any, Optional

class ModelProvider(ABC):
    @abstractmethod
    async def generate_stream(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs
    ) -> AsyncIterator[str]:
        pass

    @abstractmethod
    async def generate(
        self,
        messages: List[Dict[str, str]],
        model: str,
        **kwargs
    ) -> Dict[str, Any]:
        pass
