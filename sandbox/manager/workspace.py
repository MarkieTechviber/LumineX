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
