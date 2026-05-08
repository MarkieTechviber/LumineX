from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from .providers.unified import UnifiedLiteLLMProvider
from .agents.base import BaseAgent
import json

app = FastAPI(title="Luminex Core API")
provider = UnifiedLiteLLMProvider()

@app.get("/health")
async def health():
    return {"status": "ok", "engine": "Luminex Core"}

@app.websocket("/ws/agent")
async def agent_websocket(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            payload = json.loads(data)

            prompt = payload.get("prompt")
            model = payload.get("model", "gpt-4o")

            agent = BaseAgent(provider, model)

            async for event in agent.run_stream(prompt):
                await websocket.send_json(event)

    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        print(f"Error: {e}")
        await websocket.send_json({"type": "error", "content": str(e)})
