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
