"""ComfyUI Management Module"""

import os
import json
import requests
import subprocess
import time
from typing import Dict, List, Optional, Any
import yaml
from pathlib import Path


class ComfyUIManager:
    def __init__(self, config_path: str = "configs/config.yaml"):
        self.config = self._load_config(config_path)
        self.base_url = (
            f"http://{self.config['server']['host']}:{self.config['server']['port']}"
        )
        self.comfyui_dir = Path(self.config["paths"]["comfyui"])

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        with open(config_path, "r") as f:
            return yaml.safe_load(f)

    def is_running(self) -> bool:
        """Check if ComfyUI server is running"""
        try:
            response = requests.get(f"{self.base_url}/system_stats", timeout=5)
            return response.status_code == 200
        except:
            return False

    def get_status(self) -> Optional[Dict[str, Any]]:
        """Get ComfyUI server status"""
        if not self.is_running():
            return None

        try:
            response = requests.get(f"{self.base_url}/system_stats")
            return response.json()
        except:
            return None

    def queue_prompt(
        self, workflow: Dict[str, Any], client_id: str = None
    ) -> Optional[str]:
        """Queue a workflow prompt"""
        if not self.is_running():
            return None

        try:
            data = {"prompt": workflow}
            if client_id:
                data["client_id"] = client_id

            response = requests.post(f"{self.base_url}/prompt", json=data)
            if response.status_code == 200:
                return response.json().get("prompt_id")
        except Exception as e:
            print(f"Failed to queue prompt: {e}")

        return None
