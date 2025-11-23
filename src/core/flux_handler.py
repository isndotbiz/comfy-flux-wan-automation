"""Flux Model Handler"""

import os
import time
import uuid
from typing import Dict, Any, Optional, List
from .comfy_manager import ComfyUIManager


class FluxHandler:
    def __init__(self, comfy_manager: ComfyUIManager):
        self.comfy = comfy_manager
        self.config = comfy_manager.config

    def create_flux_workflow(
        self,
        prompt: str,
        negative_prompt: str = "blurry, low quality, distorted",
        width: int = 1024,
        height: int = 1024,
        steps: int = 20,
        cfg: float = 7.0,
        sampler: str = "euler",
        scheduler: str = "normal",
        seed: int = None,
        model_variant: str = "dev",
        lora_path: str = None,
        lora_strength: float = 1.0,
    ) -> Dict[str, Any]:
        """Create Flux workflow"""

        if seed is None:
            seed = int(time.time())

        workflow = {
            "1": {
                "inputs": {"width": width, "height": height, "batch_size": 1},
                "class_type": "EmptyLatentImage",
            },
            "2": {
                "inputs": {"text": prompt, "clip": ["11", 0]},
                "class_type": "CLIPTextEncode",
            },
            "3": {
                "inputs": {"text": negative_prompt, "clip": ["11", 0]},
                "class_type": "CLIPTextEncode",
            },
            "4": {
                "inputs": {
                    "seed": seed,
                    "steps": steps,
                    "cfg": cfg,
                    "sampler_name": sampler,
                    "scheduler": scheduler,
                    "denoise": 1.0,
                    "model": ["10", 0],
                    "positive": ["2", 0],
                    "negative": ["3", 0],
                    "latent_image": ["1", 0],
                },
                "class_type": "KSampler",
            },
            "5": {
                "inputs": {"samples": ["4", 0], "vae": ["12", 0]},
                "class_type": "VAEDecode",
            },
            "6": {
                "inputs": {
                    "filename_prefix": f"flux_{model_variant}_{int(time.time())}",
                    "images": ["5", 0],
                },
                "class_type": "SaveImage",
            },
            "10": {
                "inputs": {"unet_name": self.config["models"]["flux"][model_variant]},
                "class_type": "UNETLoader",
            },
            "11": {
                "inputs": {
                    "clip_name1": self.config["models"]["clip"]["t5"],
                    "clip_name2": self.config["models"]["clip"]["clip_l"],
                },
                "class_type": "DualCLIPLoader",
            },
            "12": {
                "inputs": {"vae_name": self.config["models"]["vae"]["flux"]},
                "class_type": "VAELoader",
            },
        }

        if lora_path:
            workflow["13"] = {
                "inputs": {
                    "lora_name": lora_path,
                    "strength_model": lora_strength,
                    "strength_clip": lora_strength,
                    "model": ["10", 0],
                    "clip": ["11", 0],
                },
                "class_type": "LoraLoader",
            }

            workflow["4"]["inputs"]["model"] = ["13", 0]
            workflow["2"]["inputs"]["clip"] = ["13", 1]
            workflow["3"]["inputs"]["clip"] = ["13", 1]

        return workflow

    def generate_image(self, prompt: str, **kwargs) -> Optional[str]:
        """Generate image using Flux"""
        workflow = self.create_flux_workflow(prompt, **kwargs)
        client_id = str(uuid.uuid4())

        prompt_id = self.comfy.queue_prompt(workflow, client_id)
        return prompt_id if prompt_id else None
