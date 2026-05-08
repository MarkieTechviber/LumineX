from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from .providers.unified import UnifiedLiteLLMProvider
from .agents.base import BaseAgent
from .agents.tools import ToolRegistry
from .agents.core_tools import WriteFileTool, ReadFileTool, RunCodeTool
from sandbox.manager.workspace import Workspace
import json

app = FastAPI(title="Luminex Core API")
provider = UnifiedLiteLLMProvider()

@app.get("/health")
async def health():
    return {"status": "ok", "engine": "Luminex Core"}

@app.websocket("/ws/agent")
async def agent_websocket(websocket: WebSocket):
    await websocket.accept()

    # Provision workspace for the session
    workspace = Workspace()
    workspace.provision()

    # Initialize tool registry
    registry = ToolRegistry()
    registry.register_tool(WriteFileTool(workspace))
    registry.register_tool(ReadFileTool(workspace))
    registry.register_tool(RunCodeTool(workspace))

    try:
        while True:
            data = await websocket.receive_text()
            payload = json.loads(data)

            prompt = payload.get("prompt")
            model = payload.get("model", "gpt-4o")

            agent = BaseAgent(provider, model, tools=registry)

            async for event in agent.run_stream(prompt):
                await websocket.send_json(event)

    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        print(f"Error: {e}")
        await websocket.send_json({"type": "error", "content": str(e)})
    finally:
        workspace.destroy()
