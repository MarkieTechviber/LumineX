# Luminex AI Platform: Full Source Code & Architecture (v3 - Complete)

## 1. File Tree
```text
luminex/
├── IMPLEMENTATION_PLAN.md    # Architecture & Design Doc
├── docker-compose.yml        # Orchestration
├── .gitignore                # Repository hygiene
├── gateway/                  # Node.js API Gateway
│   ├── src/
│   │   └── index.ts          # Gateway Logic & WebSocket Proxy
│   ├── Dockerfile
│   └── package.json
├── core/                     # Python AI Engine
│   ├── app/
│   │   ├── main.py           # FastAPI entry point & Session Mgmt
│   │   ├── agents/
│   │   │   ├── base.py       # Iterative ReAct Agent Loop
│   │   │   ├── tools.py      # Tool Abstractions
│   │   │   ├── core_tools.py # File/Code Tool Implementations
│   │   │   └── workspace_state.py # Persistent State Tracking
│   │   ├── providers/
│   │   │   ├── base.py       # Provider abstraction
│   │   │   └── unified.py    # LiteLLM implementation
│   │   └── rag/
│   │       └── engine.py     # RAG reference logic
│   ├── tests/
│   │   ├── test_providers.py # Provider tests
│   │   └── test_agent_loop.py # Agent Loop verification
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/                 # Next.js Application
│   ├── app/
│   │   ├── page.tsx          # Main Chat UI
│   │   ├── layout.tsx        # App layout
│   │   └── globals.css       # Styles
│   ├── Dockerfile
│   ├── tailwind.config.js
│   ├── postcss.config.js
│   └── package.json
└── sandbox/                  # Sandbox Environment
    ├── manager/
    │   ├── docker_manager.py # Docker SDK wrapper
    │   └── workspace.py      # Secure Workspace logic (Base64 hardened)
    └── runtimes/
        └── Dockerfile.python # Agent runtime image
```

---

## 2. Infrastructure & Orchestration
### docker-compose.yml
```yaml
version: '3.8'

services:
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_GATEWAY_URL=http://localhost:3001
    depends_on:
      - gateway

  gateway:
    build: ./gateway
    ports:
      - "3001:3001"
    environment:
      - REDIS_URL=redis://redis:6379
      - CORE_WS_URL=ws://core:8000/ws/agent
    depends_on:
      - redis
      - core

  core:
    build: ./core
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql+asyncpg://luminex:luminex@db:5432/luminex
      - REDIS_URL=redis://redis:6379
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
    depends_on:
      - db
      - redis

  db:
    image: ankane/pgvector
    environment:
      - POSTGRES_USER=luminex
      - POSTGRES_PASSWORD=luminex
      - POSTGRES_DB=luminex
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

volumes:
  postgres_data:
```

---

## 3. Gateway Layer (Node.js/TypeScript)
### gateway/src/index.ts
```typescript
import express from 'express';
import { createServer } from 'http';
import { Server } from 'socket.io';
import WebSocket from 'ws';
import cors from 'cors';
import dotenv from 'dotenv';

dotenv.config();

const app = express();
app.use(cors());
app.use(express.json());

const httpServer = createServer(app);
const io = new Server(httpServer, {
  cors: {
    origin: "*",
    methods: ["GET", "POST"]
  }
});

const CORE_WS_URL = process.env.CORE_WS_URL || 'ws://core:8000/ws/agent';

io.on('connection', (socket) => {
  console.log('Client connected:', socket.id);

  socket.on('message', (payload) => {
    console.log('Proxying request to core:', payload);

    const coreWs = new WebSocket(CORE_WS_URL);

    coreWs.on('open', () => {
      coreWs.send(JSON.stringify(payload));
    });

    coreWs.on('message', (data) => {
      const event = JSON.parse(data.toString());
      socket.emit(event.type, event);
    });

    coreWs.on('error', (err) => {
      console.error('Core WebSocket error:', err);
      socket.emit('error', { content: 'Failed to connect to AI core' });
    });

    coreWs.on('close', () => {
      console.log('Core connection closed');
    });

    socket.on('disconnect', () => {
      if (coreWs.readyState === WebSocket.OPEN) {
        coreWs.close();
      }
    });
  });
});

const PORT = process.env.PORT || 3001;
httpServer.listen(PORT, () => {
  console.log(`Gateway listening on port ${PORT}`);
});
```

---

## 4. AI Core Layer (Python)
### core/app/main.py
```python
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
```

### core/app/agents/base.py
```python
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
```

---

## 5. Frontend Layer (Next.js/React)
### frontend/Dockerfile
```dockerfile
FROM node:20-slim

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .
RUN npm run build

EXPOSE 3000

CMD ["npm", "start"]
```

### frontend/app/page.tsx
```tsx
"use client";

import React, { useState, useEffect, useRef } from 'react';
import { io, Socket } from 'socket.io-client';
import { Send, Terminal, Search, Code, Brain, Layout, Activity } from 'lucide-react';

export default function LuminexApp() {
  const [messages, setMessages] = useState<any[]>([]);
  const [input, setInput] = useState("");
  const [mode, setMode] = useState("agent");
  const [status, setStatus] = useState("Ready");
  const socketRef = useRef<Socket | null>(null);

  useEffect(() => {
    socketRef.current = io('http://localhost:3001');

    socketRef.current.on('token', (data) => {
      setMessages((prev) => {
        const last = prev[prev.length - 1];
        if (last && last.role === 'assistant') {
          return [...prev.slice(0, -1), { ...last, content: last.content + data.content }];
        }
        return [...prev, { role: 'assistant', content: data.content }];
      });
    });

    socketRef.current.on('status', (data) => {
      setStatus(data.content);
    });

    return () => {
      socketRef.current?.disconnect();
    };
  }, []);

  const handleSend = () => {
    if (!input.trim()) return;
    setMessages([...messages, { role: 'user', content: input }]);
    socketRef.current?.emit('message', { prompt: input, mode });
    setInput("");
  };

  return (
    <div className="flex h-screen bg-slate-950 text-slate-100 overflow-hidden font-sans">
      {/* Sidebar */}
      <div className="w-16 border-r border-slate-800 flex flex-col items-center py-4 gap-6 bg-slate-900/50">
        <div className="text-blue-500 font-bold text-xl mb-4">L</div>
        <ModeIcon icon={<Search size={20} />} active={mode === 'search'} onClick={() => setMode('search')} />
        <ModeIcon icon={<Code size={20} />} active={mode === 'agent'} onClick={() => setMode('agent')} />
        <ModeIcon icon={<Layout size={20} />} active={mode === 'builder'} onClick={() => setMode('builder')} />
        <ModeIcon icon={<Brain size={20} />} active={mode === 'reasoning'} onClick={() => setMode('reasoning')} />
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col relative">
        <header className="h-14 border-b border-slate-800 flex items-center px-6 justify-between bg-slate-950/80 backdrop-blur">
          <div className="flex items-center gap-2">
            <span className="font-semibold capitalize">{mode} Mode</span>
            <span className="text-xs px-2 py-0.5 rounded-full bg-blue-500/10 text-blue-400 border border-blue-500/20">{status}</span>
          </div>
          <Activity size={18} className="text-slate-500" />
        </header>

        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          {messages.map((msg, i) => (
            <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-[80%] p-4 rounded-2xl ${msg.role === 'user' ? 'bg-blue-600' : 'bg-slate-800 border border-slate-700'}`}>
                <pre className="whitespace-pre-wrap font-sans">{msg.content}</pre>
              </div>
            </div>
          ))}
        </div>

        <div className="p-4 bg-slate-950">
          <div className="max-w-4xl mx-auto relative">
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSend()}
              placeholder={`Ask Luminex anything...`}
              className="w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-4 pr-12 focus:outline-none focus:border-blue-500 transition-colors"
            />
            <button
              onClick={handleSend}
              className="absolute right-3 top-3 p-2 bg-blue-600 rounded-lg hover:bg-blue-500 transition-colors"
            >
              <Send size={18} />
            </button>
          </div>
        </div>
      </div>

      {/* Artifact Panel (Mock) */}
      <div className="w-96 border-l border-slate-800 bg-slate-900/30 hidden lg:flex flex-col">
        <div className="h-14 border-b border-slate-800 flex items-center px-4 font-medium">Artifacts & Canvas</div>
        <div className="flex-1 p-4 flex items-center justify-center text-slate-500 flex-col gap-2">
          <Layout size={48} className="opacity-20" />
          <p className="text-sm">No artifacts generated yet</p>
        </div>
      </div>
    </div>
  );
}

function ModeIcon({ icon, active, onClick }: { icon: any, active: boolean, onClick: () => void }) {
  return (
    <button
      onClick={onClick}
      className={`p-3 rounded-xl transition-all ${active ? 'bg-blue-600 text-white shadow-lg shadow-blue-600/20' : 'text-slate-400 hover:bg-slate-800 hover:text-white'}`}
    >
      {icon}
    </button>
  );
}
```

---

## 6. Sandbox Layer
### sandbox/manager/workspace.py
```python
import uuid
import time
import base64
from .docker_manager import SandboxManager

class Workspace:
    def __init__(self, workspace_id: str = None):
        self.id = workspace_id or str(uuid.uuid4())
        self.manager = SandboxManager()
        self.container_id = None

    def provision(self):
        # Use a more capable image if possible, but stick to slim for speed in reference
        container = self.manager.create_container(
            image="python:3.11-slim",
            mem_limit="1g"
        )
        self.container_id = container.id

        # Setup workspace directory
        self.manager.execute_command(self.container_id, "mkdir -p /workspace")
        return self.container_id

    def run_code(self, code: str):
        if not self.container_id:
            raise RuntimeError("Workspace not provisioned")

        encoded_code = base64.b64encode(code.encode('utf-8')).decode('utf-8')
        filename = f"script_{int(time.time())}.py"

        # Write to /workspace
        self.manager.execute_command(
            self.container_id,
            f"bash -c \"echo {encoded_code} | base64 -d > /workspace/{filename}\""
        )

        # Execute and capture stdout/stderr
        result = self.manager.execute_command(
            self.container_id,
            f"python3 /workspace/{filename}"
        )
        return result

    def destroy(self):
        if self.container_id:
            try:
                self.manager.cleanup(self.container_id)
            except:
                pass
```
