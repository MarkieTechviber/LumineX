# Luminex AI Platform: Full Source Code & Architecture

## 1. File Tree
```text
luminex/
├── IMPLEMENTATION_PLAN.md    # Architecture & Design Doc
├── docker-compose.yml        # Orchestration
├── .gitignore                # Repository hygiene
├── gateway/                  # Node.js API Gateway
│   ├── src/
│   │   └── index.ts          # Gateway Logic & Proxy
│   ├── Dockerfile
│   └── package.json
├── core/                     # Python AI Engine
│   ├── app/
│   │   ├── main.py           # FastAPI entry point
│   │   ├── agents/
│   │   │   └── base.py       # Agent Loop logic
│   │   ├── providers/
│   │   │   ├── base.py       # Provider abstraction
│   │   │   └── unified.py    # LiteLLM implementation
│   │   └── rag/
│   │       └── engine.py     # RAG reference logic
│   ├── tests/
│   │   └── test_providers.py # Provider tests
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/                 # Next.js Application
│   ├── app/
│   │   ├── page.tsx          # Main Chat UI
│   │   ├── layout.tsx        # App layout
│   │   └── globals.css       # Styles
│   ├── tailwind.config.js
│   ├── postcss.config.js
│   └── package.json
└── sandbox/                  # Sandbox Environment
    ├── manager/
    │   ├── docker_manager.py # Docker SDK wrapper
    │   └── workspace.py      # Secure Workspace logic
    └── runtimes/
        └── Dockerfile.python # Agent runtime image
```

---

## 2. Core Documentation
### IMPLEMENTATION_PLAN.md
# Luminex: Production-Grade AI Platform Implementation Plan

## 1. Executive Summary
Luminex is an independent, production-grade AI platform designed for developers and creators. It synthesizes the best architectural patterns from modern AI systems (OpenAI, Anthropic, Cursor, Perplexity, Lovable) into a unified, modular, and containerized "Super-App."

### Core Philosophy
- **Independence**: Not just a wrapper, but a full orchestration and agentic runtime.
- **Polyglot Power**: Node.js for real-time streaming; Python for AI/ML and Agentic logic.
- **Infrastructure-Agnostic**: Docker-first, ready for Kubernetes.
- **Provider-Agnostic**: Unified interface for Cloud and Local models.

---

## 2. System Architecture

### 2.1 Layered Overview
```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              FRONTEND LAYER                                  │
│  (Next.js, React, Tailwind, Lucide, Framer Motion)                          │
│  • Mode Switcher • Streaming Chat • Artifact Canvas • Agent Logs • Files    │
└─────────────────────────────────────┬───────────────────────────────────────┘
                                     │ (WebSocket / HTTP/2)
┌─────────────────────────────────────▼───────────────────────────────────────┐
│                           GATEWAY LAYER (Node.js)                            │
│  • Session Manager • Rate Limiting • MCP Client • WebSocket Bridge           │
│  • Auth • Event Dispatcher • Provider Routing                                │
└─────────────────────────────────────┬───────────────────────────────────────┘
                                     │ (gRPC / Internal API)
┌─────────────────────────────────────▼───────────────────────────────────────┐
│                             CORE LAYER (Python)                              │
│  • Agent Loop (ReAct/Plan-and-Execute) • RAG Engine • Reasoning Pipeline     │
│  • Unified Provider Adapter (OpenAI, Anthropic, Ollama, vLLM)                │
│  • Memory Manager (Postgres + pgvector)                                      │
└─────────────────────────────────────┬───────────────────────────────────────┘
                                     │ (Docker SDK / API)
┌─────────────────────────────────────▼───────────────────────────────────────┐
│                            SANDBOX RUNTIME LAYER                             │
│  • Container Manager • Resource Isolation • Network Egress Control           │
│  • Tool Execution Host • Ephemeral Workspaces                                │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Technology Stack
- **Frontend**: Next.js 14 (App Router), TypeScript, Shadcn/UI, Tailwind CSS.
- **Gateway**: Node.js, Fastify/Express, Socket.io (WebSockets), `zod` (Validation).
- **Core**: Python 3.11+, FastAPI, Pydantic, LangChain/LangGraph (Orchestration), LiteLLM (Provider Abstraction).
- **Storage**: PostgreSQL (Data + pgvector), Redis (Sessions + Pub/Sub).
- **Infrastructure**: Docker, Docker Compose, Nginx (Proxy).

---

## 3. Operational Modes

### 3.1 Search / Research Mode (Perplexity-inspired)
- **Engine**: Multi-pass RAG loop.
- **Logic**: Query intent parsing -> Multi-source retrieval -> Relevance reranking -> Synthesis with citations.
- **Tools**: Web Search (Tavily/Serper), Academic APIs, Local vector store.

### 3.2 Coding / Agent Mode (Cursor/Claude Code-inspired)
- **Engine**: Observe-Plan-Act-Verify loop.
- **Logic**: Codebase indexing (Tree-sitter) -> Multi-file edit coordination -> Auto-debugging.
- **Tools**: Filesystem access, LSP integration, Terminal execution.

### 3.3 Builder / UI Mode (Lovable/v0-inspired)
- **Engine**: AST-based code generation.
- **Logic**: Design prompt -> Component selection (Shadcn) -> Code synthesis -> Sandbox preview.
- **Tools**: Vite-based preview server, React component library.

### 3.4 Deep Reasoning Mode (OpenAI o-series-inspired)
- **Engine**: Hidden Chain-of-Thought (CoT).
- **Logic**: Extended thinking tokens -> Process Reward Model (PRM) filtering -> Self-correction.

---

## 4. Engineering Logic & Components

### 4.1 The Unified Provider Interface
A standardized abstraction for interacting with different LLMs.
```python
class ModelProvider(ABC):
    @abstractmethod
    async def generate(self, prompt: str, stream: bool = True) -> AsyncIterator[str]:
        pass

class OpenAIAdapter(ModelProvider): ...
class AnthropicAdapter(ModelProvider): ...
class LocalOllamaAdapter(ModelProvider): ...
```

### 4.2 The Agent Loop (ReAct Pattern)
1. **Input**: User prompt + Context.
2. **Thought**: LLM generates a plan and selects a tool.
3. **Action**: Sandbox execution of the tool.
4. **Observation**: Capture tool output (stdout, file changes, etc.).
5. **Verify/Reflect**: LLM evaluates the result and decides if the task is complete.

### 4.3 RAG Pipeline (pgvector)
- **Ingestion**: Document -> Hierarchical Chunking -> Embedding (OpenAI/HuggingFace) -> pgvector storage.
- **Retrieval**: Query Embedding -> Vector Similarity Search -> Cross-Encoder Reranking -> Context Injection.

---

## 5. Security & Sandboxing

### 5.1 Docker-First Isolation
- Every agent task runs in an ephemeral Docker container.
- **Resource Limits**: CPU (0.5 - 2 cores), RAM (512MB - 2GB).
- **Network**: Restricted egress (whitelist) or no internet access for untrusted code.
- **Volume Mounting**: Read-only project files, write-only `/tmp` or specific workspace folders.

### 5.2 Sandbox Manager Logic
- Programmatic lifecycle management using Docker SDK.
- Health monitoring and automatic cleanup of stale containers.

---

## 6. Project Structure

```text
luminex/
├── gateway/              # Node.js Streaming & API Gateway
│   ├── src/
│   │   ├── websocket/    # Real-time orchestration
│   │   ├── routes/       # Auth & Session management
│   │   └── mcp/          # Model Context Protocol integration
│   └── package.json
├── core/                 # Python AI Engine
│   ├── app/
│   │   ├── agents/       # Agent Loop & Logic
│   │   ├── providers/    # Model Adapters (Unified Interface)
│   │   ├── rag/          # RAG Pipeline & Embeddings
│   │   └── reasoning/    # CoT & Thinking logic
│   └── requirements.txt
├── frontend/             # Next.js Application
│   ├── components/       # Chat, Canvas, Artifacts, FileTree
│   ├── store/            # State management (Zustand/Jotai)
│   └── app/              # Next.js Routes
├── sandbox/              # Sandbox Management
│   ├── manager/          # Python/Node.js Sandbox API
│   └── runtimes/         # Dockerfiles for specific languages/tasks
├── infra/                # Infrastructure & Config
│   ├── postgres/         # Init scripts & pgvector config
│   ├── redis/            # Configuration
│   └── nginx/            # Proxy & SSL
└── docker-compose.yml    # Production-ready orchestration
```

---

## 7. Implementation Phases

### Phase 1: Foundation (The Skeleton)
- Setup Docker Compose with Postgres and Redis.
- Implement basic Gateway (Node) and Core (Python) communication.
- Create Unified Provider Interface (OpenAI + Ollama).

### Phase 2: The Agent & Sandbox
- Implement the Docker Sandbox Manager.
- Build the core ReAct agent loop in Python.
- Connect Frontend streaming UI to the Agent loop.

### Phase 3: Modes & Memory
- Implement Search mode with RAG (pgvector).
- Implement Builder mode with Artifact rendering.
- Add long-term memory for user preferences.

### Phase 4: Hardening & Scaling
- Add MCP server integration.
- Implement rate limiting and security policies.
- Optimize streaming (WebSockets/HTTP2).

---

## 3. Infrastructure & Orchestration
### docker-compose.yml
```yaml
version: '3.8'

services:
  gateway:
    build: ./gateway
    ports:
      - "3001:3001"
    environment:
      - REDIS_URL=redis://redis:6379
      - CORE_API_URL=http://core:8000
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

### .gitignore
```text
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Node.js
node_modules/
dist/
build/
.npm
npm-debug.log*
yarn-debug.log*
yarn-error.log*
.env

# Next.js
.next/
out/

# Docker
.dockerignore

# OS
.DS_Store
Thumbs.db
```

---

## 4. Gateway Layer (Node.js/TypeScript)
### gateway/package.json
```json
{
  "name": "luminex-gateway",
  "version": "1.0.0",
  "description": "Luminex API Gateway",
  "main": "dist/index.js",
  "scripts": {
    "start": "node dist/index.js",
    "dev": "ts-node-dev src/index.ts",
    "build": "tsc"
  },
  "dependencies": {
    "@types/ws": "^8.18.1",
    "axios": "^1.6.0",
    "cors": "^2.8.5",
    "dotenv": "^16.3.1",
    "express": "^4.18.2",
    "ioredis": "^5.3.2",
    "socket.io": "^4.7.2",
    "ws": "^8.20.0",
    "zod": "^3.22.4"
  },
  "devDependencies": {
    "@types/cors": "^2.8.15",
    "@types/express": "^4.17.20",
    "@types/node": "^20.8.9",
    "ts-node-dev": "^2.0.0",
    "typescript": "^5.2.2"
  }
}
```

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

### gateway/Dockerfile
```dockerfile
FROM node:20-slim

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .
RUN npm run build

EXPOSE 3001

CMD ["npm", "start"]
```

---

## 5. AI Core Layer (Python)
### core/requirements.txt
```text
fastapi
uvicorn
pydantic
openai
anthropic
litellm
langchain
langgraph
sqlalchemy[asyncio]
asyncpg
pgvector
redis
python-multipart
python-dotenv
docker
```

### core/app/main.py
```python
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
```

### core/app/agents/base.py
```python
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
```

### core/app/providers/base.py
```python
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
```

### core/app/providers/unified.py
```python
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
```

### core/app/rag/engine.py
```python
from typing import List, Dict, Any
import sqlalchemy
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://luminex:luminex@db:5432/luminex")

class RAGEngine:
    def __init__(self):
        self.engine = create_async_engine(DATABASE_URL)
        self.async_session = sessionmaker(
            self.engine, expire_on_commit=False, class_=AsyncSession
        )

    async def search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        # This is a reference implementation for vector search
        # In a real scenario, we'd use pgvector's <=> operator
        # SELECT content FROM documents ORDER BY embedding <=> %s LIMIT %s
        return [
            {"content": f"Reference context for: {query}", "source": "local_db"}
        ]

    async def ingest(self, content: str, metadata: Dict[str, Any]):
        # Logic to chunk, embed, and store in pgvector
        pass
```

### core/tests/test_providers.py
```python
import pytest
from app.providers.unified import UnifiedLiteLLMProvider

@pytest.mark.asyncio
async def test_unified_provider_instantiation():
    provider = UnifiedLiteLLMProvider()
    assert provider is not None
```

### core/Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## 6. Frontend Layer (Next.js/React)
### frontend/package.json
```json
{
  "name": "luminex-frontend",
  "version": "0.1.0",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint"
  },
  "dependencies": {
    "next": "14.0.0",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "lucide-react": "^0.288.0",
    "socket.io-client": "^4.7.2",
    "framer-motion": "^10.16.4",
    "clsx": "^2.0.0",
    "tailwind-merge": "^1.14.0"
  },
  "devDependencies": {
    "typescript": "^5.2.2",
    "@types/node": "^20.8.9",
    "@types/react": "^18.2.33",
    "@types/react-dom": "^18.2.14",
    "autoprefixer": "^10.4.16",
    "postcss": "^8.4.31",
    "tailwindcss": "^3.3.5"
  }
}
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

### frontend/app/layout.tsx
```tsx
import './globals.css'
import type { Metadata } from 'next'
import { Inter } from 'next/font/google'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Luminex AI',
  description: 'Production-Grade AI Platform',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>{children}</body>
    </html>
  )
}
```

### frontend/app/globals.css
```css
@tailwind base;
@tailwind components;
@tailwind utilities;
```

### frontend/tailwind.config.js
```javascript
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
```

### frontend/postcss.config.js
```javascript
module.exports = {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
```

---

## 7. Sandbox Layer
### sandbox/manager/docker_manager.py
```python
import docker
import os
from typing import Optional

class SandboxManager:
    def __init__(self):
        try:
            self.client = docker.from_env()
        except Exception:
            print("Docker client not found. Sandbox mode limited.")
            self.client = None

    def create_container(
        self,
        image: str = "python:3.11-slim",
        command: Optional[str] = None,
        mem_limit: str = "512m",
        cpu_period: int = 100000,
        cpu_quota: int = 50000, # 0.5 CPU
    ):
        if not self.client:
            raise RuntimeError("Docker not available")

        container = self.client.containers.run(
            image,
            command=command,
            detach=True,
            mem_limit=mem_limit,
            cpu_period=cpu_period,
            cpu_quota=cpu_quota,
            network_disabled=True, # Isolation by default
        )
        return container

    def execute_command(self, container_id: str, command: str):
        container = self.client.containers.get(container_id)
        exit_code, output = container.exec_run(command)
        return {
            "exit_code": exit_code,
            "output": output.decode('utf-8')
        }

    def cleanup(self, container_id: str):
        container = self.client.containers.get(container_id)
        container.stop()
        container.remove()
```

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
        # In a real environment, we would use a pre-built image
        container = self.manager.create_container(
            image="python:3.11-slim",
            mem_limit="1g"
        )
        self.container_id = container.id
        return self.container_id

    def run_code(self, code: str):
        if not self.container_id:
            raise RuntimeError("Workspace not provisioned")

        # Use base64 to safely transfer code and avoid shell injection
        encoded_code = base64.b64encode(code.encode('utf-8')).decode('utf-8')
        filename = f"script_{int(time.time())}.py"

        # Write file using base64 decoding inside the container
        self.manager.execute_command(
            self.container_id,
            f"bash -c \"echo {encoded_code} | base64 -d > /tmp/{filename}\""
        )

        # Execute the script
        result = self.manager.execute_command(
            self.container_id,
            f"python3 /tmp/{filename}"
        )
        return result

    def destroy(self):
        if self.container_id:
            self.manager.cleanup(self.container_id)
```

### sandbox/runtimes/Dockerfile.python
```dockerfile
# Base image for Luminex Agents
FROM python:3.11-slim

WORKDIR /workspace

# Install common build tools
RUN apt-get update && apt-get install -i -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Default command
CMD ["bash"]
```
