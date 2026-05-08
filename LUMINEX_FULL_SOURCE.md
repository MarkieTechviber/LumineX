# Luminex AI Platform: Full Source Code & Architecture (v2)

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

---

## 4. Gateway Layer (Node.js/TypeScript)
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

## 5. AI Core Layer (Python)
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

### core/app/agents/tools.py
```python
from abc import ABC, abstractmethod
from typing import Dict, Any, Type, List
import json

class BaseTool(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        pass

    @property
    @abstractmethod
    def parameters(self) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def execute(self, **kwargs) -> Any:
        pass

    def to_openai_tool(self) -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
        }

class ToolRegistry:
    def __init__(self):
        self.tools: Dict[str, BaseTool] = {}

    def register_tool(self, tool: BaseTool):
        self.tools[tool.name] = tool

    def get_tool(self, name: str) -> BaseTool:
        return self.tools.get(name)

    def get_openai_tools(self) -> List[Dict[str, Any]]:
        return [tool.to_openai_tool() for tool in self.tools.values()]
```

### core/app/agents/core_tools.py
```python
import base64
from typing import Dict, Any
from .tools import BaseTool

class WriteFileTool(BaseTool):
    name = "write_file"
    description = "Writes content to a file in the workspace"
    parameters = {
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Path to the file"},
            "content": {"type": "string", "description": "Content to write"}
        },
        "required": ["path", "content"]
    }

    def __init__(self, workspace):
        self.workspace = workspace

    async def execute(self, path: str, content: str) -> str:
        try:
            # We use the workspace's secure method
            # For simplicity in this tool, we assume workspace handles the transfer
            # In real implementation, we'd call workspace.write(path, content)
            encoded_content = base64.b64encode(content.encode('utf-8')).decode('utf-8')
            self.workspace.manager.execute_command(
                self.workspace.container_id,
                f"bash -c \"echo {encoded_content} | base64 -d > {path}\""
            )
            return f"Successfully wrote to {path}"
        except Exception as e:
            return f"Error writing file: {str(e)}"

class ReadFileTool(BaseTool):
    name = "read_file"
    description = "Reads content from a file in the workspace"
    parameters = {
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Path to the file"}
        },
        "required": ["path"]
    }

    def __init__(self, workspace):
        self.workspace = workspace

    async def execute(self, path: str) -> str:
        try:
            result = self.workspace.manager.execute_command(
                self.workspace.container_id,
                f"cat {path}"
            )
            if result['exit_code'] == 0:
                return result['output']
            else:
                return f"Error reading file: {result['output']}"
        except Exception as e:
            return f"Error reading file: {str(e)}"

class RunCodeTool(BaseTool):
    name = "run_code"
    description = "Executes python code in the sandbox environment"
    parameters = {
        "type": "object",
        "properties": {
            "code": {"type": "string", "description": "Python code to execute"}
        },
        "required": ["code"]
    }

    def __init__(self, workspace):
        self.workspace = workspace

    async def execute(self, code: str) -> Dict[str, Any]:
        return self.workspace.run_code(code)
```

### core/app/agents/workspace_state.py
```python
from typing import Dict, List, Any
import os

class WorkspaceState:
    def __init__(self, root_dir: str = "/tmp/luminex_workspace"):
        self.root_dir = root_dir
        self.files: Dict[str, str] = {}
        self.history: List[Dict[str, Any]] = []

    def track_change(self, path: str, content: str, change_type: str = "write"):
        self.files[path] = content
        self.history.append({
            "path": path,
            "type": change_type,
            "timestamp": os.times()[4]
        })

    def get_file_tree(self) -> List[str]:
        return list(self.files.keys())

    def get_summary(self) -> str:
        files = self.get_file_tree()
        return f"Current Workspace: {len(files)} files tracked. Tree: {', '.join(files)}"
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
