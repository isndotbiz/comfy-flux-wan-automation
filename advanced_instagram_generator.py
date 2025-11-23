#!/usr/bin/env python3
"""
Advanced Instagram Generator with Ollama + LoRA Integration
Combines AI prompt optimization with LoRA models for high-quality Instagram images
"""
import json
import time
import requests
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import random


class OllamaOptimizer:
    def __init__(self, host: str = "host.docker.internal", port: int = 11434):
        self.base_url = f"http://{host}:{port}"
        self.model = "mistral"  # or "llama2", "codellama", etc.

    def is_available(self) -> bool:
        """Check if Ollama is running"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False

    def optimize_prompt(
        self,
        base_prompt: str,
        style: str = "instagram",
        lora_triggers: List[str] = None,
    ) -> Tuple[str, str]:
        """Optimize prompt using Ollama/Mistral"""
        if not self.is_available():
            return self._fallback_enhance(base_prompt, lora_triggers)

        # Create context-aware system prompt
        lora_context = ""
        if lora_triggers:
            lora_context = f"Include these style keywords naturally: {', '.join(lora_triggers[:3])}"

        system_prompt = f"""You are an expert at creating prompts for Flux/WAN AI image generation models, specifically for {style} style images. 

Your task: Transform the user's basic prompt into an optimized, detailed prompt that will produce stunning results.

Guidelines:
- Keep core subject/concept from original prompt
- Add photographic and aesthetic details
- Include lighting, composition, quality keywords
- {lora_context}
- Output ONLY the optimized prompt, no explanations
- Maximum 100 words
- Focus on visual details that enhance image quality

Example transformation:
Input: "woman portrait"
Output: "professional portrait of beautiful woman, soft natural lighting, shallow depth of field, 85mm lens, high resolution, photorealistic, detailed skin texture, elegant composition, studio quality, bokeh background"
"""

        payload = {
            "model": self.model,
            "prompt": base_prompt,
            "system": system_prompt,
            "stream": False,
            "options": {"temperature": 0.7, "top_p": 0.9, "max_tokens": 150},
        }

        try:
            response = requests.post(
                f"{self.base_url}/api/generate", json=payload, timeout=30
            )
            if response.status_code == 200:
                result = response.json()
                optimized_prompt = result.get("response", "").strip()

                # Generate negative prompt
                negative_prompt = self._generate_negative_prompt()

                return optimized_prompt, negative_prompt
            else:
                return self._fallback_enhance(base_prompt, lora_triggers)
        except Exception as e:
            print(f"⚠️ Ollama optimization failed, using fallback: {e}")
            return self._fallback_enhance(base_prompt, lora_triggers)

    def _fallback_enhance(
        self, prompt: str, lora_triggers: List[str] = None
    ) -> Tuple[str, str]:
        """Fallback prompt enhancement"""
        quality_words = [
            "high quality",
            "detailed",
            "professional",
            "photorealistic",
            "sharp focus",
            "beautiful lighting",
            "masterpiece",
            "8K resolution",
            "hyperdetailed",
            "award winning photography",
        ]

        instagram_style = [
            "instagram style",
            "social media ready",
            "aesthetic",
            "trendy",
            "modern photography",
            "lifestyle photo",
            "influencer style",
        ]

        # Combine with trigger words if available
        enhancement_words = quality_words + instagram_style
        if lora_triggers:
            enhancement_words.extend(lora_triggers[:2])

        selected_enhancements = random.sample(
            enhancement_words, min(5, len(enhancement_words))
        )
        enhanced_prompt = f"{prompt}, {', '.join(selected_enhancements)}"

        negative_prompt = "blurry, low quality, distorted, amateur, bad anatomy, deformed, ugly, pixelated, watermark, text, signature"

        return enhanced_prompt, negative_prompt

    def _generate_negative_prompt(self) -> str:
        """Generate comprehensive negative prompt"""
        return (
            "blurry, low quality, distorted, amateur, bad anatomy, deformed, ugly, pixelated, "
            "watermark, text, signature, oversaturated, noise, artifacts, jpeg artifacts, "
            "bad lighting, overexposed, underexposed, unrealistic, cartoonish"
        )


class AdvancedInstagramGenerator:
    def __init__(self):
        self.base_url = "http://127.0.0.1:8188"
        self.optimizer = OllamaOptimizer()
        self.output_dir = Path(
            "/workspace/comfy-flux-wan-automation/workflows/advanced"
        )
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Load available LoRAs
        self.loras = self._load_available_loras()

    def _load_available_loras(self) -> List[Dict]:
        """Load available LoRA models with metadata"""
        lora_dir = Path("/workspace/ComfyUI/models/loras")
        loras = []

        for lora_file in lora_dir.glob("*.safetensors"):
            metadata_file = lora_file.with_suffix(".json")

            if metadata_file.exists():
                try:
                    with open(metadata_file, "r") as f:
                        metadata = json.load(f)
                    metadata["file_path"] = str(lora_file)
                    loras.append(metadata)
                except:
                    pass
            else:
                # Basic info for files without metadata
                loras.append(
                    {
                        "filename": lora_file.name,
                        "file_path": str(lora_file),
                        "name": lora_file.stem,
                        "description": "LoRA model",
                        "trigger_words": [],
                        "tags": [],
                    }
                )

        return loras

    def get_suggested_loras(self, prompt: str) -> List[Dict]:
        """Suggest LoRAs based on prompt content"""
        prompt_lower = prompt.lower()
        suitable_loras = []

        # Keywords that suggest LoRA usage
        portrait_keywords = ["woman", "girl", "portrait", "face", "model", "person"]
        realistic_keywords = ["realistic", "photo", "photography", "professional"]

        for lora in self.loras:
            lora_score = 0
            lora_tags = [tag.lower() for tag in lora.get("tags", [])]
            lora_name = lora["name"].lower()

            # Score based on relevance
            if any(keyword in prompt_lower for keyword in portrait_keywords):
                if any(
                    tag in ["portrait", "realistic", "photography"] for tag in lora_tags
                ):
                    lora_score += 3
                if "portrait" in lora_name or "realistic" in lora_name:
                    lora_score += 2

            if any(keyword in prompt_lower for keyword in realistic_keywords):
                if any(
                    tag in ["realistic", "photography", "photo"] for tag in lora_tags
                ):
                    lora_score += 2

            if lora_score > 0:
                lora["relevance_score"] = lora_score
                suitable_loras.append(lora)

        # Sort by relevance and return top 5
        suitable_loras.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
        return suitable_loras[:5]

    def create_advanced_workflow(
        self,
        prompt: str,
        negative_prompt: str,
        lora_file: str = None,
        lora_strength: float = 0.8,
        trigger_words: List[str] = None,
        width: int = 1024,
        height: int = 1024,
        steps: int = 28,
        cfg: float = 7.0,
    ) -> Dict:
        """Create advanced workflow with optional LoRA"""

        # Enhance prompt with trigger words if using LoRA
        final_prompt = prompt
        if lora_file and trigger_words:
            trigger_text = ", ".join(trigger_words[:3])
            final_prompt = f"{trigger_text}, {prompt}"

        timestamp = int(time.time())
        workflow_id = f"adv_ig_{timestamp}"

        base_workflow = {
            "4": {
                "inputs": {"width": width, "height": height, "batch_size": 1},
                "class_type": "EmptyLatentImage",
            },
            "5": {
                "inputs": {
                    "seed": timestamp % 1000000,
                    "steps": steps,
                    "cfg": cfg,
                    "sampler_name": "euler",
                    "scheduler": "normal",
                    "denoise": 1.0,
                    "model": ["7", 0] if lora_file else ["7", 0],
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
                "inputs": {"filename_prefix": workflow_id, "images": ["8", 0]},
                "class_type": "SaveImage",
            },
        }

        # Add LoRA nodes if specified
        if lora_file:
            # LoRA loader node
            base_workflow["3"] = {
                "inputs": {
                    "lora_name": lora_file,
                    "strength_model": lora_strength,
                    "strength_clip": lora_strength,
                    "model": ["7", 0],
                    "clip": ["6", 0],
                },
                "class_type": "LoraLoader",
            }

            # Update text encoding to use LoRA output
            base_workflow["1"] = {
                "inputs": {
                    "text": final_prompt,
                    "clip": ["3", 1],  # Connect to LoRA clip output
                },
                "class_type": "CLIPTextEncode",
            }

            base_workflow["2"] = {
                "inputs": {
                    "text": negative_prompt,
                    "clip": ["3", 1],  # Connect to LoRA clip output
                },
                "class_type": "CLIPTextEncode",
            }

            # Update sampler to use LoRA model
            base_workflow["5"]["inputs"]["model"] = ["3", 0]

        else:
            # Standard text encoding without LoRA
            base_workflow["1"] = {
                "inputs": {"text": final_prompt, "clip": ["6", 0]},
                "class_type": "CLIPTextEncode",
            }

            base_workflow["2"] = {
                "inputs": {"text": negative_prompt, "clip": ["6", 0]},
                "class_type": "CLIPTextEncode",
            }

        return base_workflow

    def generate_instagram_batch(
        self, prompts: List[str], use_lora: bool = True, auto_select_lora: bool = True
    ) -> List[str]:
        """Generate batch of Instagram images with optimization"""

        if not prompts:
            print("❌ No prompts provided")
            return []

        results = []
        available_loras = self.loras if use_lora else []

        print(f"🎨 Starting advanced batch generation for {len(prompts)} prompts...")
        print(
            f"🤖 Ollama optimization: {'✅' if self.optimizer.is_available() else '❌ (fallback)'}"
        )
        print(f"🎭 LoRAs available: {len(available_loras)}")

        for i, base_prompt in enumerate(prompts, 1):
            print(f"\n📸 Processing {i}/{len(prompts)}: '{base_prompt[:50]}...'")

            # Select LoRA for this prompt
            selected_lora = None
            trigger_words = []

            if use_lora and available_loras:
                if auto_select_lora:
                    suggested_loras = self.get_suggested_loras(base_prompt)
                    if suggested_loras:
                        selected_lora = suggested_loras[0]
                        trigger_words = selected_lora.get("trigger_words", [])
                        print(f"🎭 Selected LoRA: {selected_lora['name']}")
                        if trigger_words:
                            print(f"📝 Trigger words: {', '.join(trigger_words[:3])}")
                else:
                    # Use random LoRA
                    selected_lora = random.choice(available_loras)
                    trigger_words = selected_lora.get("trigger_words", [])

            # Optimize prompt
            optimized_prompt, negative_prompt = self.optimizer.optimize_prompt(
                base_prompt, "instagram", trigger_words
            )

            print(f"✨ Optimized: '{optimized_prompt[:80]}...'")

            # Create workflow
            lora_file = None
            lora_strength = 0.8

            if selected_lora:
                lora_file = Path(selected_lora["file_path"]).name

            workflow = self.create_advanced_workflow(
                prompt=optimized_prompt,
                negative_prompt=negative_prompt,
                lora_file=lora_file,
                lora_strength=lora_strength,
                trigger_words=trigger_words,
                steps=30,  # Higher quality
                cfg=7.5,
            )

            # Save workflow and metadata
            timestamp = int(time.time())
            workflow_file = self.output_dir / f"advanced_instagram_{timestamp}_{i}.json"

            metadata = {
                "original_prompt": base_prompt,
                "optimized_prompt": optimized_prompt,
                "negative_prompt": negative_prompt,
                "lora_used": selected_lora["name"] if selected_lora else None,
                "lora_file": lora_file,
                "trigger_words": trigger_words,
                "timestamp": timestamp,
                "generation_settings": {
                    "steps": 30,
                    "cfg": 7.5,
                    "resolution": "1024x1024",
                },
            }

            # Save workflow
            with open(workflow_file, "w") as f:
                json.dump(workflow, f, indent=2)

            # Save metadata
            metadata_file = workflow_file.with_suffix(".meta.json")
            with open(metadata_file, "w") as f:
                json.dump(metadata, f, indent=2)

            # Queue to ComfyUI
            try:
                response = requests.post(
                    f"{self.base_url}/prompt", json={"prompt": workflow}
                )
                if response.status_code == 200:
                    prompt_id = response.json().get("prompt_id")
                    print(f"✅ Queued! ID: {prompt_id}")
                    results.append(prompt_id)
                else:
                    print(f"❌ Queue failed: {response.status_code}")
            except Exception as e:
                print(f"❌ Error queuing: {e}")

            # Brief pause between requests
            time.sleep(2)

        print(f"\n🎉 Batch complete! {len(results)}/{len(prompts)} successfully queued")
        print(f"📁 Workflows saved to: {self.output_dir}")
        print("🌐 Monitor progress at: http://localhost:8188")
        print("🖼️ Check outputs in: /workspace/ComfyUI/output")

        return results


def main():
    generator = AdvancedInstagramGenerator()

    print("🎨 Advanced Instagram Generator with AI + LoRA")
    print("=" * 50)
    print(
        f"🤖 Ollama status: {'✅ Connected' if generator.optimizer.is_available() else '❌ Offline (using fallback)'}"
    )
    print(f"🎭 LoRAs available: {len(generator.loras)}")

    if generator.loras:
        print("\n📋 Available LoRAs:")
        for i, lora in enumerate(generator.loras[:5], 1):
            print(f"  {i}. {lora['name']}")
            if lora.get("trigger_words"):
                print(f"     Triggers: {', '.join(lora['trigger_words'][:3])}")

    print("\n🎯 Generation modes:")
    print("1. Single optimized prompt")
    print("2. Batch generation (multiple prompts)")
    print("3. Instagram girl variations")

    choice = input("\nSelect mode (1-3): ").strip()

    if choice == "1":
        prompt = input("Enter your prompt: ").strip()
        if prompt:
            results = generator.generate_instagram_batch(
                [prompt], use_lora=True, auto_select_lora=True
            )
            if results:
                print(f"\n✅ Generated with ID: {results[0]}")

    elif choice == "2":
        print("Enter prompts (one per line, empty line to finish):")
        prompts = []
        while True:
            prompt = input().strip()
            if not prompt:
                break
            prompts.append(prompt)

        if prompts:
            use_lora = input("Use LoRAs? (y/n, default y): ").strip().lower() != "n"
            results = generator.generate_instagram_batch(prompts, use_lora=use_lora)

    elif choice == "3":
        # Instagram girl variations
        base_prompts = [
            "beautiful young woman with natural makeup, soft lighting",
            "professional portrait of elegant woman, studio lighting",
            "casual lifestyle photo of attractive girl, golden hour",
            "fashion portrait of stylish woman, modern aesthetic",
            "candid photo of smiling girl, natural beauty",
        ]

        print(f"🚀 Generating {len(base_prompts)} Instagram variations...")
        results = generator.generate_instagram_batch(
            base_prompts, use_lora=True, auto_select_lora=True
        )

        if results:
            print(f"\n🎉 All {len(results)} variations queued successfully!")


if __name__ == "__main__":
    main()
