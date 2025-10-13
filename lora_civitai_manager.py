#!/usr/bin/env python3
"""
LoRA and CivitAI Manager with Ollama Optimization
Downloads and manages LoRAs from CivitAI with AI-optimized prompts
"""
import json
import time
import requests
import os
import hashlib
from pathlib import Path
from typing import Dict, List, Optional
from urllib.parse import urlparse


class CivitAIManager:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("CIVITAI_TOKEN")
        self.base_url = "https://civitai.com/api/v1"
        self.lora_dir = Path("/workspace/ComfyUI/models/loras")
        self.lora_dir.mkdir(parents=True, exist_ok=True)

    def search_loras(self, query: str, limit: int = 10) -> List[Dict]:
        """Search for LoRAs on CivitAI"""
        params = {
            "limit": limit,
            "query": query,
            "types": "LORA",
            "sort": "Highest Rated",
            "period": "Month",
        }

        try:
            response = requests.get(
                f"{self.base_url}/models", params=params, timeout=30
            )
            if response.status_code == 200:
                return response.json().get("items", [])
            else:
                print(f"❌ CivitAI search failed: {response.status_code}")
                return []
        except Exception as e:
            print(f"❌ CivitAI connection error: {e}")
            return []

    def get_popular_instagram_loras(self) -> List[Dict]:
        """Get popular Instagram/portrait LoRAs"""
        queries = ["instagram", "portrait", "realistic", "photography", "woman"]
        all_loras = []

        for query in queries:
            loras = self.search_loras(query, 5)
            all_loras.extend(loras)

        # Remove duplicates and sort by rating
        unique_loras = {}
        for lora in all_loras:
            if lora["id"] not in unique_loras:
                unique_loras[lora["id"]] = lora

        sorted_loras = sorted(
            unique_loras.values(),
            key=lambda x: x.get("stats", {}).get("rating", 0),
            reverse=True,
        )

        return sorted_loras[:15]  # Top 15

    def download_lora(self, model_id: int, version_id: int = None) -> Optional[str]:
        """Download LoRA from CivitAI"""
        try:
            # Get model details
            model_response = requests.get(f"{self.base_url}/models/{model_id}")
            if model_response.status_code != 200:
                print(f"❌ Failed to get model details: {model_response.status_code}")
                return None

            model_data = model_response.json()
            model_versions = model_data.get("modelVersions", [])

            if not model_versions:
                print("❌ No versions available for this model")
                return None

            # Use specified version or latest
            if version_id:
                version = next(
                    (v for v in model_versions if v["id"] == version_id),
                    model_versions[0],
                )
            else:
                version = model_versions[0]  # Latest version

            # Get download file
            files = version.get("files", [])
            download_file = next((f for f in files if f["type"] == "Model"), None)

            if not download_file:
                print("❌ No downloadable model file found")
                return None

            download_url = download_file["downloadUrl"]
            filename = download_file["name"]

            # Create safe filename
            safe_name = "".join(c for c in filename if c.isalnum() or c in "._-")
            file_path = self.lora_dir / safe_name

            print(f"📥 Downloading {filename}...")

            # Download file
            headers = {}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"

            response = requests.get(download_url, headers=headers, stream=True)
            response.raise_for_status()

            with open(file_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            print(f"✅ Downloaded: {file_path}")

            # Save metadata
            metadata = {
                "model_id": model_id,
                "version_id": version["id"],
                "name": model_data["name"],
                "description": model_data.get("description", ""),
                "tags": model_data.get("tags", []),
                "trigger_words": version.get("trainedWords", []),
                "base_model": version.get("baseModel", ""),
                "download_date": time.time(),
                "filename": safe_name,
            }

            metadata_path = file_path.with_suffix(".json")
            with open(metadata_path, "w") as f:
                json.dump(metadata, f, indent=2)

            return str(file_path)

        except Exception as e:
            print(f"❌ Download failed: {e}")
            return None

    def list_downloaded_loras(self) -> List[Dict]:
        """List all downloaded LoRAs with metadata"""
        loras = []

        for lora_file in self.lora_dir.glob("*.safetensors"):
            metadata_file = lora_file.with_suffix(".json")

            if metadata_file.exists():
                with open(metadata_file, "r") as f:
                    metadata = json.load(f)
                metadata["file_path"] = str(lora_file)
                loras.append(metadata)
            else:
                # Basic info for files without metadata
                loras.append(
                    {
                        "filename": lora_file.name,
                        "file_path": str(lora_file),
                        "name": lora_file.stem,
                        "description": "No metadata available",
                        "trigger_words": [],
                        "tags": [],
                    }
                )

        return loras


class LoRAOptimizedGenerator:
    def __init__(self):
        self.civitai = CivitAIManager()
        self.base_url = "http://127.0.0.1:8188"

    def create_lora_workflow(
        self,
        prompt: str,
        lora_file: str,
        lora_strength: float = 0.8,
        trigger_words: List[str] = None,
    ) -> Dict:
        """Create workflow with LoRA integration"""

        # Enhance prompt with trigger words
        enhanced_prompt = prompt
        if trigger_words:
            trigger_text = ", ".join(trigger_words[:3])  # Use first 3 trigger words
            enhanced_prompt = f"{trigger_text}, {prompt}"

        timestamp = int(time.time())

        return {
            "1": {
                "inputs": {
                    "text": enhanced_prompt,
                    "clip": ["3", 1],  # Connect to LoRA output
                },
                "class_type": "CLIPTextEncode",
            },
            "2": {
                "inputs": {
                    "text": "blurry, low quality, distorted, amateur, bad anatomy, deformed",
                    "clip": ["3", 1],
                },
                "class_type": "CLIPTextEncode",
            },
            "3": {
                "inputs": {
                    "lora_name": lora_file,
                    "strength_model": lora_strength,
                    "strength_clip": lora_strength,
                    "model": ["7", 0],
                    "clip": ["6", 0],
                },
                "class_type": "LoraLoader",
            },
            "4": {
                "inputs": {"width": 1024, "height": 1024, "batch_size": 1},
                "class_type": "EmptyLatentImage",
            },
            "5": {
                "inputs": {
                    "seed": timestamp % 1000000,
                    "steps": 28,
                    "cfg": 7.0,
                    "sampler_name": "euler",
                    "scheduler": "normal",
                    "denoise": 1.0,
                    "model": ["3", 0],  # Use LoRA-modified model
                    "positive": ["1", 0],
                    "negative": ["2", 0],
                    "latent_image": ["4", 0],
                },
                "class_type": "KSampler",
            },
            "6": {
                "inputs": {
                    "clip_name1": "umt5-xxl-enc-bf16.safetensors",
                    "clip_name2": "open-clip-xlm-roberta-large-vit-huge-14_visual_fp16.safetensors",
                    "type": "flux",
                },
                "class_type": "DualCLIPLoader",
            },
            "7": {
                "inputs": {
                    "unet_name": "Wan2_1-InfiniTetalk-Single_fp16.safetensors",
                    "weight_dtype": "default",
                },
                "class_type": "UNETLoader",
            },
            "8": {
                "inputs": {"samples": ["5", 0], "vae": ["9", 0]},
                "class_type": "VAEDecode",
            },
            "9": {
                "inputs": {"vae_name": "Wan2_1_VAE_bf16.safetensors"},
                "class_type": "VAELoader",
            },
            "10": {
                "inputs": {
                    "filename_prefix": f"lora_{Path(lora_file).stem}_{timestamp}",
                    "images": ["8", 0],
                },
                "class_type": "SaveImage",
            },
        }

    def generate_with_lora(
        self, prompt: str, lora_info: Dict, strength: float = 0.8
    ) -> Optional[str]:
        """Generate image using specific LoRA"""
        lora_filename = Path(lora_info["file_path"]).name
        trigger_words = lora_info.get("trigger_words", [])

        print(f"🎨 Generating with LoRA: {lora_info['name']}")
        print(
            f"📝 Trigger words: {', '.join(trigger_words) if trigger_words else 'None'}"
        )

        workflow = self.create_lora_workflow(
            prompt, lora_filename, strength, trigger_words
        )

        try:
            response = requests.post(
                f"{self.base_url}/prompt", json={"prompt": workflow}
            )
            if response.status_code == 200:
                prompt_id = response.json().get("prompt_id")
                print(f"✅ Queued with LoRA! ID: {prompt_id}")
                return prompt_id
            else:
                print(f"❌ Queue failed: {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ Error: {e}")
            return None


def main():
    print("🎨 LoRA & CivitAI Manager with AI Optimization")
    print("=" * 50)

    civitai = CivitAIManager()
    generator = LoRAOptimizedGenerator()

    print("\n🤖 Options:")
    print("1. Browse popular Instagram LoRAs")
    print("2. Search CivitAI for specific LoRA")
    print("3. Download LoRA by model ID")
    print("4. Generate with downloaded LoRAs")
    print("5. List downloaded LoRAs")

    choice = input("\nSelect option (1-5): ").strip()

    if choice == "1":
        print("\n🔍 Finding popular Instagram LoRAs...")
        loras = civitai.get_popular_instagram_loras()

        if loras:
            print(f"\n📋 Top {len(loras)} Instagram LoRAs:")
            for i, lora in enumerate(loras[:10], 1):
                rating = lora.get("stats", {}).get("rating", 0)
                downloads = lora.get("stats", {}).get("downloadCount", 0)
                print(f"{i:2d}. {lora['name']}")
                print(
                    f"    ID: {lora['id']} | Rating: {rating:.1f} | Downloads: {downloads:,}"
                )
                print(f"    Tags: {', '.join(lora.get('tags', [])[:5])}")
        else:
            print("❌ No LoRAs found")

    elif choice == "2":
        query = input("Enter search query: ").strip()
        if query:
            print(f"\n🔍 Searching for '{query}'...")
            loras = civitai.search_loras(query, 10)

            for i, lora in enumerate(loras, 1):
                rating = lora.get("stats", {}).get("rating", 0)
                print(
                    f"{i:2d}. {lora['name']} (ID: {lora['id']}) | Rating: {rating:.1f}"
                )

    elif choice == "3":
        try:
            model_id = int(input("Enter CivitAI model ID: ").strip())
            print(f"\n📥 Downloading model {model_id}...")
            file_path = civitai.download_lora(model_id)
            if file_path:
                print(f"✅ Successfully downloaded to: {file_path}")
            else:
                print("❌ Download failed")
        except ValueError:
            print("❌ Invalid model ID")

    elif choice == "4":
        # Generate with LoRAs
        downloaded_loras = civitai.list_downloaded_loras()

        if not downloaded_loras:
            print("❌ No LoRAs downloaded. Download some first!")
            return

        print(f"\n📋 Available LoRAs ({len(downloaded_loras)}):")
        for i, lora in enumerate(downloaded_loras, 1):
            print(f"{i:2d}. {lora['name']}")
            if lora.get("trigger_words"):
                print(f"    Triggers: {', '.join(lora['trigger_words'][:3])}")

        try:
            lora_idx = int(input("\nSelect LoRA number: ").strip()) - 1
            if 0 <= lora_idx < len(downloaded_loras):
                selected_lora = downloaded_loras[lora_idx]

                prompt = input("Enter your prompt: ").strip()
                if prompt:
                    strength = float(
                        input("LoRA strength (0.1-1.0, default 0.8): ").strip() or "0.8"
                    )

                    prompt_id = generator.generate_with_lora(
                        prompt, selected_lora, strength
                    )
                    if prompt_id:
                        print("\n✅ Generation started!")
                        print("🌐 Monitor at: http://localhost:8188")
            else:
                print("❌ Invalid selection")
        except (ValueError, IndexError):
            print("❌ Invalid input")

    elif choice == "5":
        downloaded_loras = civitai.list_downloaded_loras()

        if downloaded_loras:
            print(f"\n📋 Downloaded LoRAs ({len(downloaded_loras)}):")
            for i, lora in enumerate(downloaded_loras, 1):
                print(f"{i:2d}. {lora['name']}")
                print(f"    File: {Path(lora['file_path']).name}")
                if lora.get("description"):
                    print(f"    Description: {lora['description'][:100]}...")
                if lora.get("trigger_words"):
                    print(f"    Trigger words: {', '.join(lora['trigger_words'])}")
                print()
        else:
            print("❌ No LoRAs downloaded yet")


if __name__ == "__main__":
    main()
