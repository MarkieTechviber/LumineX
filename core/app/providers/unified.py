from typing import AsyncIterator, List, Dict, Any
from litellm import acompletion
from .base import ModelProvider

class UnifiedLiteLLMProvider(ModelProvider):
    """
    Uses LiteLLM to provide a unified interface for 100+ LLMs
    (OpenAI, Anthropic, Gemini, Ollama, etc.)
    """

    async def generate_stream(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs
    ) -> AsyncIterator[str]:
        response = await acompletion(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
            **kwargs
        )
        async for chunk in response:
            content = chunk.choices[0].delta.content
            if content:
                yield content

    async def generate(
        self,
        messages: List[Dict[str, str]],
        model: str,
        **kwargs
    ) -> Dict[str, Any]:
        response = await acompletion(
            model=model,
            messages=messages,
            **kwargs
        )
        return response.to_dict()
