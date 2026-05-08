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
