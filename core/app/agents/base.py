from typing import List, Dict, Any, Optional, AsyncIterator
from pydantic import BaseModel
import json

class AgentState(BaseModel):
    messages: List[Dict[str, str]] = []
    plan: List[str] = []
    context: Dict[str, Any] = {}
    completed: bool = False

class BaseAgent:
    def __init__(self, provider, model: str):
        self.provider = provider
        self.model = model

    async def run_stream(self, prompt: str) -> AsyncIterator[Dict[str, Any]]:
        state = AgentState(messages=[{"role": "user", "content": prompt}])

        # 1. Planning Phase
        yield {"type": "status", "content": "Planning task..."}
        plan_prompt = f"Develop a step-by-step plan for the following task: {prompt}. Return as a JSON list of strings."
        plan_response = await self.provider.generate(
            messages=[{"role": "system", "content": "You are a planning assistant. Output ONLY a JSON list."},
                      {"role": "user", "content": plan_prompt}],
            model=self.model,
            response_format={ "type": "json_object" }
        )

        try:
            # Simple heuristic to extract list
            content = plan_response['choices'][0]['message']['content']
            state.plan = json.loads(content).get("plan", [])
        except:
            state.plan = [prompt]

        yield {"type": "plan", "content": state.plan}

        # 2. Execution Phase (ReAct Loop)
        for step in state.plan:
            yield {"type": "status", "content": f"Executing: {step}"}

            async for chunk in self.provider.generate_stream(
                messages=state.messages + [{"role": "system", "content": f"Now execute this step: {step}"}],
                model=self.model
            ):
                yield {"type": "token", "content": chunk}

            # In a real loop, we'd append assistant response to state.messages

        yield {"type": "done", "content": "Task completed successfully."}
