import pytest
from unittest.mock import AsyncMock, MagicMock
from app.agents.base import BaseAgent
from app.agents.tools import ToolRegistry
from app.agents.core_tools import RunCodeTool

@pytest.mark.asyncio
async def test_agent_loop_iteration():
    # Mock provider
    mock_provider = MagicMock()
    mock_provider.generate = AsyncMock(return_value={
        "choices": [{
            "message": {
                "role": "assistant",
                "content": "I will run some code.",
                "tool_calls": [{
                    "id": "call_1",
                    "function": {
                        "name": "run_code",
                        "arguments": '{"code": "print(1+1)"}'
                    }
                }]
            }
        }]
    })

    # Mock workspace
    mock_workspace = MagicMock()
    # run_code is NOT async in the implementation, but let's check
    mock_workspace.run_code.return_value = {"exit_code": 0, "output": "2"}

    registry = ToolRegistry()
    registry.register_tool(RunCodeTool(mock_workspace))

    agent = BaseAgent(mock_provider, "gpt-4o", tools=registry)

    events = []
    async for event in agent.run_stream("What is 1+1?"):
        events.append(event)
        if len(events) > 10: break # Safety

    # Check if tool was called
    assert any(e["type"] == "observation" and e["tool"] == "run_code" for e in events)
    assert any(e["content"] == "I will run some code." for e in events if e["type"] == "token")
