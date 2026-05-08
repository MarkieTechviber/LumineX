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
