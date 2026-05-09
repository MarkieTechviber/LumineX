# Luminex AI Platform: Full Source Code & Architecture (v4 - Complete)

## 1. File Tree
```text
luminex/
├── IMPLEMENTATION_PLAN.md    # Architecture & Design Doc
├── luminex_ui.html           # Expert UI/UX Standalone Design
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

## 3. Expert UI/UX Design
### luminex_ui.html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Luminex AI Platform</title>
    <style>
        :root {
            --bg: #f5f3ee;
            --surface-1: #f9f7f2;
            --surface-2: #f0ece3;
            --blue: #4a7fa5;
            --blue-tint: #eef4fa;
            --blue-soft: #dbeaf5;
            --wheat: #c8a96e;
            --wheat-tint: #faf4e8;
            --wheat-soft: #f5ead5;
            --text: #2c2a25;
            --text-muted: #7a7268;
            --text-hint: #a89e92;
            --border: rgba(100,90,70,0.12);
            --code-bg: #2a2924;
            --transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
        }

        .mode-dark {
            --bg: #1e1d1a;
            --surface-1: #232220;
            --surface-2: #2a2924;
            --blue: #7ab3d4;
            --blue-tint: #192530;
            --blue-soft: #1e2e3a;
            --wheat: #c8a96e;
            --wheat-tint: #251f12;
            --wheat-soft: #2e2618;
            --text: #ede8df;
            --text-muted: #8a8070;
            --text-hint: #5a5448;
            --border: rgba(200,180,140,0.10);
        }

        .mode-oled {
            --bg: #000000;
            --surface-1: #050504;
            --surface-2: #0c0b09;
            --blue: #6aaed0;
            --blue-tint: #070f18;
            --wheat: #b8995e;
            --wheat-tint: #110e05;
            --text: #e8e0d0;
            --text-muted: #706858;
            --border: rgba(180,160,120,0.08);
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        }

        body {
            background-color: var(--bg);
            color: var(--text);
            height: 100vh;
            display: flex;
            overflow: hidden;
            transition: var(--transition);
        }

        /* Sidebar */
        .sidebar {
            width: 200px;
            border-right: 1px solid var(--border);
            display: flex;
            flex-col: column;
            flex-direction: column;
            background-color: var(--surface-1);
        }

        .logo-mark {
            padding: 24px;
            display: flex;
            align-items: center;
            gap: 12px;
        }

        .logo-icon {
            width: 32px;
            height: 32px;
            background-color: var(--blue-soft);
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: var(--blue);
            font-weight: bold;
        }

        .logo-text {
            font-weight: 600;
            letter-spacing: -0.5px;
            color: var(--text);
        }

        .nav-section {
            padding: 0 12px;
            margin-bottom: 24px;
        }

        .nav-item {
            padding: 8px 12px;
            border-radius: 6px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 4px;
            transition: var(--transition);
            font-size: 14px;
            color: var(--text-muted);
        }

        .nav-item:hover {
            background-color: var(--surface-2);
            color: var(--text);
        }

        .nav-item.on {
            background-color: var(--blue-tint);
            color: var(--blue);
            font-weight: 500;
        }

        .nav-item.on .badge {
            background-color: var(--blue);
            color: white;
        }

        .badge {
            font-size: 10px;
            padding: 2px 6px;
            border-radius: 10px;
            background-color: var(--surface-2);
            color: var(--text-muted);
        }

        .history-section {
            flex: 1;
            padding: 0 12px;
            overflow-y: auto;
        }

        .history-label {
            font-size: 11px;
            text-transform: uppercase;
            letter-spacing: 1px;
            color: var(--text-hint);
            margin: 12px;
        }

        .history-item {
            padding: 6px 12px;
            font-size: 13px;
            color: var(--text-muted);
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            cursor: pointer;
            border-radius: 4px;
        }

        .history-item:hover {
            background-color: var(--surface-2);
        }

        .user-footer {
            padding: 16px;
            border-top: 1px solid var(--border);
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .avatar {
            width: 28px;
            height: 28px;
            background-color: var(--wheat-soft);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            color: var(--wheat);
            font-size: 12px;
            font-weight: bold;
        }

        /* Main Chat */
        .main-chat {
            flex: 1;
            display: flex;
            flex-direction: column;
            background-color: var(--bg);
        }

        .top-bar {
            height: 56px;
            border-bottom: 1px solid var(--border);
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0 24px;
        }

        .theme-switcher {
            display: flex;
            gap: 4px;
            background-color: var(--surface-2);
            padding: 4px;
            border-radius: 8px;
        }

        .theme-btn {
            padding: 4px 12px;
            font-size: 12px;
            border-radius: 6px;
            cursor: pointer;
            border: none;
            background: none;
            color: var(--text-muted);
            transition: var(--transition);
        }

        .theme-btn.active {
            background-color: var(--blue-tint);
            color: var(--blue);
            box-shadow: 0 1px 2px rgba(0,0,0,0.05);
        }

        .mode-pills {
            display: flex;
            gap: 12px;
        }

        .mode-pill {
            display: flex;
            align-items: center;
            gap: 6px;
            font-size: 13px;
            color: var(--text-muted);
        }

        .dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
        }

        .chat-container {
            flex: 1;
            padding: 24px;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            gap: 24px;
        }

        .message {
            max-width: 85%;
            padding: 12px 16px;
            border-radius: 12px;
            line-height: 1.5;
            font-size: 15px;
            position: relative;
        }

        .message.user {
            align-self: flex-end;
            background-color: var(--blue-tint);
            color: var(--text);
            border-bottom-right-radius: 2px;
        }

        .message.ai {
            align-self: flex-start;
            background-color: var(--surface-1);
            border: 1px solid var(--border);
            border-bottom-left-radius: 2px;
        }

        .plan-card {
            background-color: var(--wheat-tint);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 12px;
            margin-top: 12px;
        }

        .plan-header {
            font-size: 12px;
            font-weight: 600;
            color: var(--wheat);
            text-transform: uppercase;
            margin-bottom: 8px;
        }

        code {
            display: block;
            background-color: var(--code-bg);
            color: #dcd7ba;
            padding: 12px;
            border-radius: 6px;
            font-family: "JetBrains Mono", monospace;
            font-size: 13px;
            margin: 12px 0;
            overflow-x: auto;
        }

        .typing {
            display: none;
            padding: 12px 16px;
            background-color: var(--surface-1);
            border: 1px solid var(--border);
            border-radius: 12px;
            width: fit-content;
            color: var(--blue);
            font-size: 13px;
            animation: pulse 1.5s infinite;
        }

        @keyframes pulse {
            0% { opacity: 0.6; }
            50% { opacity: 1; }
            100% { opacity: 0.6; }
        }

        .input-area {
            padding: 24px;
            border-top: 1px solid var(--border);
        }

        .input-wrapper {
            background-color: var(--surface-1);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 12px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.02);
        }

        textarea {
            width: 100%;
            border: none;
            background: none;
            resize: none;
            height: 60px;
            color: var(--text);
            font-size: 15px;
            outline: none;
        }

        .input-meta {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-top: 8px;
        }

        .meta-tools {
            display: flex;
            gap: 16px;
            color: var(--text-hint);
            font-size: 12px;
        }

        .send-btn {
            background-color: var(--blue);
            color: white;
            border: none;
            padding: 6px 16px;
            border-radius: 6px;
            font-size: 13px;
            font-weight: 500;
            cursor: pointer;
            transition: var(--transition);
        }

        .send-btn:hover {
            opacity: 0.9;
        }

        /* Artifact Panel */
        .artifact-panel {
            width: 240px;
            border-left: 1px solid var(--border);
            background-color: var(--surface-1);
            display: flex;
            flex-direction: column;
            padding: 16px;
            gap: 16px;
        }

        .panel-title {
            font-size: 13px;
            font-weight: 600;
            color: var(--text-muted);
            margin-bottom: 4px;
        }

        .file-card {
            background-color: var(--bg);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 10px;
            display: flex;
            flex-direction: column;
            gap: 8px;
            transition: var(--transition);
        }

        .file-card:hover {
            border-color: var(--blue);
        }

        .file-info {
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .file-type {
            font-size: 10px;
            padding: 2px 4px;
            border-radius: 4px;
            font-weight: bold;
        }

        .type-blue { background-color: var(--blue-soft); color: var(--blue); }
        .type-wheat { background-color: var(--wheat-soft); color: var(--wheat); }

        .file-name { font-size: 12px; font-weight: 500; color: var(--text); }

        .metrics-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 8px;
        }

        .metric-card {
            background-color: var(--surface-2);
            padding: 8px;
            border-radius: 6px;
            text-align: center;
        }

        .metric-value { font-size: 14px; font-weight: 600; color: var(--blue); }
        .metric-label { font-size: 10px; color: var(--text-hint); }

        .sandbox-card {
            background-color: var(--blue-tint);
            border: 1px solid var(--blue);
            border-radius: 8px;
            padding: 12px;
            color: var(--blue);
        }

        .sandbox-status {
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 12px;
            font-weight: 600;
        }

        .status-pulse {
            width: 6px;
            height: 6px;
            background-color: var(--blue);
            border-radius: 50%;
            animation: pulse 1s infinite;
        }
    </style>
</head>
<body>
    <!-- Sidebar -->
    <aside class="sidebar">
        <div class="logo-mark">
            <div class="logo-icon">L</div>
            <div class="logo-text">Luminex</div>
        </div>

        <nav class="nav-section">
            <div class="nav-item on" onclick="setMode(this)">
                Reasoning <span class="badge">o4</span>
            </div>
            <div class="nav-item" onclick="setMode(this)">
                Agent Mode <span class="badge">Active</span>
            </div>
            <div class="nav-item" onclick="setMode(this)">
                Research <span class="badge">Web</span>
            </div>
            <div class="nav-item" onclick="setMode(this)">
                Builder <span class="badge">v0</span>
            </div>
        </nav>

        <div class="history-section">
            <div class="history-label">Recent History</div>
            <div class="history-item">Designing production-grade RAG...</div>
            <div class="history-item">Implementing stateful session APIs</div>
            <div class="history-item">MCP tool integration strategies</div>
            <div class="history-item">Sandboxed execution with Firecracker</div>
        </div>

        <div class="user-footer">
            <div class="avatar">JD</div>
            <div class="logo-text" style="font-size: 13px;">James D.</div>
        </div>
    </aside>

    <!-- Main Chat -->
    <main class="main-chat">
        <header class="top-bar">
            <div class="mode-pills">
                <div class="mode-pill"><div class="dot" style="background-color: var(--blue);"></div> Reasoning</div>
                <div class="mode-pill"><div class="dot" style="background-color: var(--wheat);"></div> Tools</div>
            </div>

            <div class="theme-switcher">
                <button class="theme-btn active" onclick="setTheme('light', this)">Light</button>
                <button class="theme-btn" onclick="setTheme('dark', this)">Dark</button>
                <button class="theme-btn" onclick="setTheme('oled', this)">OLED</button>
            </div>
        </header>

        <section class="chat-container" id="chat">
            <div class="message ai">
                Hello! I'm Luminex. How can I help you architect your next agentic system today?
            </div>
        </section>

        <div class="typing" id="typing-indicator">Luminex is thinking...</div>

        <footer class="input-area">
            <div class="input-wrapper">
                <textarea id="user-input" placeholder="Compose a message..."></textarea>
                <div class="input-meta">
                    <div class="meta-tools">
                        <span>Attach +</span>
                        <span>Web Search</span>
                        <span>Artifacts</span>
                    </div>
                    <button class="send-btn" onclick="sendMessage()">Send</button>
                </div>
            </div>
        </footer>
    </main>

    <!-- Artifact Panel -->
    <aside class="artifact-panel">
        <div>
            <div class="panel-title">Active Workspace</div>
            <div class="file-card">
                <div class="file-info">
                    <span class="file-type type-blue">TS</span>
                    <span class="file-name">orchestrator.ts</span>
                </div>
                <div class="file-info" style="justify-content: space-between;">
                    <span style="font-size: 10px; color: var(--text-hint);">Modified 2m ago</span>
                    <span class="badge">97% Match</span>
                </div>
            </div>
            <div class="file-card" style="margin-top: 8px;">
                <div class="file-info">
                    <span class="file-type type-wheat">MD</span>
                    <span class="file-name">IMPLEMENTATION.md</span>
                </div>
            </div>
        </div>

        <div>
            <div class="panel-title">Session Metrics</div>
            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-value">12.4k</div>
                    <div class="metric-label">Tokens</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">4.2s</div>
                    <div class="metric-label">Latency</div>
                </div>
            </div>
        </div>

        <div class="sandbox-card">
            <div class="sandbox-status">
                <div class="status-pulse"></div>
                Sandbox Environment
            </div>
            <div style="font-size: 10px; margin-top: 8px; opacity: 0.8;">
                Runtime: Python 3.12 (Isolated)
                Memory: 124/512MB
            </div>
        </div>
    </aside>

    <script>
        const chat = document.getElementById('chat');
        const userInput = document.getElementById('user-input');
        const typingIndicator = document.getElementById('typing-indicator');

        function setTheme(theme, btn) {
            document.body.className = '';
            if (theme !== 'light') {
                document.body.classList.add('mode-' + theme);
            }

            document.querySelectorAll('.theme-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
        }

        function setMode(item) {
            document.querySelectorAll('.nav-item').forEach(i => i.classList.remove('on'));
            item.classList.add('on');
        }

        function sendMessage() {
            const text = userInput.value.trim();
            if (!text) return;

            appendMessage('user', text);
            userInput.value = '';

            // AI Logic
            typingIndicator.style.display = 'block';
            chat.scrollTop = chat.scrollHeight;

            setTimeout(() => {
                typingIndicator.style.display = 'none';
                generateAIResponse(text);
            }, 1200);
        }

        function appendMessage(role, text) {
            const div = document.createElement('div');
            div.className = `message ${role}`;
            div.innerText = text;
            chat.appendChild(div);
            chat.scrollTop = chat.scrollHeight;
        }

        function generateAIResponse(query) {
            const div = document.createElement('div');
            div.className = 'message ai';

            // Warm, cozy AI response
            let response = "That's an interesting approach to the architecture. ";

            if (query.toLowerCase().includes('code')) {
                response += "I've drafted a reference implementation for you to explore:";
                const code = document.createElement('code');
                code.innerText = "class LuminexAgent {\n  constructor(config) {\n    this.memory = new PersistentMemory();\n    this.tools = new ToolRegistry();\n  }\n\n  async plan(task) {\n    return await this.llm.reason(task);\n  }\n}";
                div.innerText = response;
                div.appendChild(code);
            } else {
                response += "I've outlined a step-by-step plan in the workspace to help us move forward with this design.";
                const plan = document.createElement('div');
                plan.className = 'plan-card';
                plan.innerHTML = `
                    <div class="plan-header">Execution Strategy</div>
                    <div style="font-size: 13px; color: var(--text-muted);">
                        1. Index codebase with tree-sitter<br>
                        2. Initialize stateful reasoning loop<br>
                        3. Execute initial sandbox test run
                    </div>
                `;
                div.innerText = response;
                div.appendChild(plan);
            }

            chat.appendChild(div);
            chat.scrollTop = chat.scrollHeight;
        }

        userInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });
    </script>
</body>
</html>

---

## 4. AI Core Layer (Python)
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

---

## 5. Gateway Layer (Node.js/TypeScript)
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

---

## 7. Setup & Deployment
### SETUP_GUIDE.md
# Luminex Setup & Deployment Guide

This guide will walk you through installing Docker and running the Luminex AI Platform on your laptop.

---

## Step 1: Install Docker on Your Laptop

Luminex runs inside **Docker**, which ensures it works the same on your machine as it does in production.

### For Windows:
1.  **Download Docker Desktop**: Go to the [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop/) page and click **"Download for Windows"**.
2.  **Install**: Run the installer. Ensure the **"Use WSL 2 instead of Hyper-V"** option is checked (recommended).
3.  **Restart**: You may need to restart your computer.
4.  **Start Docker**: Open "Docker Desktop" from your Start menu and wait for the "Engine Running" green light.

### For macOS:
1.  **Download Docker Desktop**: Go to the [Docker Desktop for Mac](https://www.docker.com/products/docker-desktop/) page. Choose **"Apple Chip"** if you have an M1/M2/M3 Mac, or **"Intel Chip"** for older Macs.
2.  **Install**: Open the `.dmg` file and drag Docker to your **Applications** folder.
3.  **Start Docker**: Open Docker from your Applications. Grant any requested permissions.

### For Linux (Ubuntu):
Run these commands in your terminal:
```bash
sudo apt-get update
sudo apt-get install docker.io docker-compose
sudo systemctl start docker
sudo systemctl enable docker
```

---

## Step 2: Configure Environment Variables

Luminex requires an API key to communicate with AI models (like GPT-4).

1.  Navigate to the `luminex` folder on your laptop.
2.  Create a file named `.env` (or open the existing one).
3.  Add your API key:
    ```env
    OPENAI_API_KEY=your_actual_key_here
    ```

---

## Step 3: Run Luminex with Docker Compose

Once Docker is running, you can launch the entire platform (Frontend, Gateway, Core, Database, and Redis) with a single command.

1.  **Open your Terminal** (or PowerShell/Command Prompt).
2.  **Navigate** to the Luminex project directory:
    ```bash
    cd path/to/luminex
    ```
3.  **Launch the platform**:
    ```bash
    docker-compose up --build
    ```
4.  **Wait**: Docker will download necessary images and build the platform. This may take a few minutes the first time.

---

## Step 4: Access the Platform

Once the terminal shows that the services are running, open your web browser:

*   **Luminex App**: [http://localhost:3000](http://localhost:3000)
*   **API Gateway**: [http://localhost:3001](http://localhost:3001)
*   **Core Engine**: [http://localhost:8000](http://localhost:8000)

---

## Step 5: Using the Expert UI

If you want to view the **Expert UI/UX Standalone Design**:
1.  Locate `luminex_ui.html` in the project folder.
2.  **Double-click** it to open it directly in your browser.
3.  Use the top-right buttons to switch between **Light, Dark, and OLED** modes.

---

## Troubleshooting
*   **Docker not running**: Ensure the Docker Desktop app is open and shows a green status.
*   **Port already in use**: If you get an error about ports 3000 or 5432, make sure you don't have other web servers or databases running on your machine.
*   **API Key missing**: If the AI doesn't respond, double-check your `.env` file for the `OPENAI_API_KEY`.
