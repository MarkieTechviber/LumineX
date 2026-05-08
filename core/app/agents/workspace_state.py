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
