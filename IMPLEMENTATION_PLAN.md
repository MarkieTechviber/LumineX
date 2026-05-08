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
