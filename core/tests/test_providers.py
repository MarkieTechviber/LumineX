import pytest
from app.providers.unified import UnifiedLiteLLMProvider

@pytest.mark.asyncio
async def test_unified_provider_instantiation():
    provider = UnifiedLiteLLMProvider()
    assert provider is not None
