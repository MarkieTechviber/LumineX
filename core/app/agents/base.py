from typing import List, Dict, Any, Optional, AsyncIterator
from pydantic import BaseModel
import json
from .tools import ToolRegistry

class AgentState(BaseModel):
    messages: List[Dict[str, str]] = []
    plan: List[str] = []
    context: Dict[str, Any] = {}
    completed: bool = False
    iteration_count: int = 0
    max_iterations: int = 10

class BaseAgent:
    def __init__(self, provider, model: str, tools: Optional[ToolRegistry] = None):
        self.provider = provider
        self.model = model
        self.tools = tools

    async def run_stream(self, prompt: str) -> AsyncIterator[Dict[str, Any]]:
        state = AgentState(messages=[
            {"role": "system", "content": "You are a production-grade AI agent. Use tools to accomplish your task. Think, plan, act, observe, and reflect. If you fail, analyze and replan."},
            {"role": "user", "content": prompt}
        ])

        while not state.completed and state.iteration_count < state.max_iterations:
            state.iteration_count += 1
            yield {"type": "status", "content": f"Iteration {state.iteration_count}: Thinking..."}

            # 1. Reasoning & Action Step
            openai_tools = self.tools.get_openai_tools() if self.tools else None

            response = await self.provider.generate(
                messages=state.messages,
                model=self.model,
                tools=openai_tools,
                tool_choice="auto" if openai_tools else None
            )

            message = response['choices'][0]['message']
            state.messages.append(message)

            if message.get("content"):
                yield {"type": "token", "content": message["content"]}

            # 2. Tool Execution Step
            if message.get("tool_calls"):
                for tool_call in message["tool_calls"]:
                    tool_name = tool_call["function"]["name"]
                    tool_args = json.loads(tool_call["function"]["arguments"])

                    yield {"type": "status", "content": f"Calling tool: {tool_name}"}

                    tool = self.tools.get_tool(tool_name)
                    if tool:
                        result = await tool.execute(**tool_args)
                        # Observation
                        state.messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call["id"],
                            "name": tool_name,
                            "content": json.dumps(result)
                        })
                        yield {"type": "observation", "tool": tool_name, "content": result}
                    else:
                        error_msg = f"Tool {tool_name} not found"
                        state.messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call["id"],
                            "name": tool_name,
                            "content": error_msg
                        })
            else:
                # No more tools called, assume task finished or needing reflection
                state.completed = True

        yield {"type": "done", "content": "Task completed."}
