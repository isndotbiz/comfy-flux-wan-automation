#!/usr/bin/env python3
"""
Advanced Batch Instagram Generator with Ollama Prompt Optimization
Generates multiple high-quality images using optimized prompts
"""
import json
import time
import requests
import sys
import os
import subprocess
from pathlib import Path
from typing import List, Dict

class OllamaPromptOptimizer:
    def __init__(self, host="host.docker.internal", port=11434):
        self.base_url = f"http://{host}:{port}"
        self.model = "mistral"
        
    def is_ollama_available(self) -> bool:
        """Check if Ollama is accessible"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            # Try localhost if host.docker.internal fails
            try:
                self.base_url = "http://localhost:11434"
                response = requests.get(f"{self.base_url}/api/tags", timeout=5)
                return response.status_code == 200
            except:
                return False
    
    def optimize_prompt(self, base_prompt: str, style: str = "instagram") -> str:
        """Use Ollama Mistral to optimize prompts for Flux/WAN generation"""
        
        optimization_prompt = f"""You are an expert AI image generation prompt engineer specializing in Flux and WAN models for creating stunning {style}-style content.

Transform this basic prompt into the absolute best practices prompt for maximum quality:
"{base_prompt}"

Requirements:
1. Use proven Flux/WAN keywords that generate high-quality results
2. Include technical photography terms for professional results  
3. Add specific lighting, composition, and style descriptors
4. Include negative prompt suggestions
5. Optimize for LoRA compatibility (Instagram/portrait styles)

Respond in this exact JSON format:
{{
    "optimized_prompt": "enhanced prompt with technical details",
    "negative_prompt": "specific things to avoid",
    "style_notes": "brief explanation of improvements",
    "recommended_settings": {{
        "steps": 25,
        "cfg": 7.5,
        "sampler": "euler"
    }}
}}

Make the prompt concise but powerful - focus on proven keywords that work best with Flux models."""

        try:
            payload = {
                "model": self.model,
                "prompt": optimization_prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.9
                }
            }
            
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return self.parse_optimization_result(result.get("response", ""))
            else:
                print(f"❌ Ollama API error: {response.status_code}")
                return self.fallback_optimization(base_prompt)
                
        except Exception as e:
            print(f"❌ Ollama connection failed: {e}")
            return self.fallback_optimization(base_prompt)
    
    def parse_optimization_result(self, response: str) -> Dict:
        """Parse Ollama response and extract optimization data"""
        try:
            # Try to find JSON in the response
            start = response.find('{')
            end = response.rfind('}') + 1
            if start >= 0 and end > start:
                json_str = response[start:end]
                return json.loads(json_str)
        except:
            pass
        
        # Fallback parsing if JSON extraction fails
        return {
            "optimized_prompt": f"{response[:200]}..." if len(response) > 200 else response,
            "negative_prompt": "blurry, low quality, distorted, amateur",
            "style_notes": "AI-optimized prompt",
            "recommended_settings": {"steps": 25, "cfg": 7.5, "sampler": "euler"}
        }
    
    def fallback_optimization(self, base_prompt: str) -> Dict:
        """Fallback optimization when Ollama isn't available"""
        enhanced_prompt = f"{base_prompt}, professional photography, high quality, detailed, sharp focus, perfect lighting, cinematic composition, 8k resolution, masterpiece"
        
        return {
            "optimized_prompt": enhanced_prompt,
            "negative_prompt": "blurry, low quality, distorted, amateur, bad lighting, pixelated, ugly, deformed, watermark",
            "style_notes": "Fallback enhancement with proven keywords",
            "recommended_settings": {"steps": 25, "cfg": 7.5, "sampler": "euler"}
        }

class AdvancedBatchGenerator:
    def __init__(self, base_url="http://127.0.0.1:8188"):
        self.base_url = base_url
        self.output_dir = Path("/workspace/ComfyUI/output")
        self.optimizer = OllamaPromptOptimizer()
        
    def check_systems(self):
        """Check if ComfyUI and Ollama are available"""
        print("🔍 Checking system availability...")
        
        # Check ComfyUI
        try:
            response = requests.get(f"{self.base_url}/system_stats", timeout=5)
            comfy_status = response.status_code == 200
        except:
            comfy_status = False
        
        # Check Ollama
        ollama_status = self.optimizer.is_ollama_available()
        
        print(f"✅ ComfyUI: {'AVAILABLE' if comfy_status else '❌ NOT AVAILABLE'}")
        print(f"🤖 Ollama: {'AVAILABLE' if ollama_status else '❌ NOT AVAILABLE'}")
        
        return comfy_status, ollama_status
    
    def create_optimized_workflow(self, optimized_data: Dict, timestamp: int) -> Dict:
        """Create workflow using optimized prompt data"""
        settings = optimized_data["recommended_settings"]
        
        return {
            "1": {
                "inputs": {
                    "text": optimized_data["optimized_prompt"],
                    "clip": ["2", 0]
                },
                "class_type": "CLIPTextEncode"
            },
            "2": {
                "inputs": {
                    "clip_name1": "umt5-xxl-enc-bf16.safetensors",
                    "clip_name2": "open-clip-xlm-roberta-large-vit-huge-14_visual_fp16.safetensors",
                    "type": "flux"
                },
                "class_type": "DualCLIPLoader"
            },
            "3": {
                "inputs": {
                    "width": 1024,
                    "height": 1024,
                    "batch_size": 1
                },
                "class_type": "EmptyLatentImage"
            },
            "4": {
                "inputs": {
                    "text": optimized_data["negative_prompt"],
                    "clip": ["2", 0]
                },
                "class_type": "CLIPTextEncode"
            },
            "5": {
                "inputs": {
                    "seed": timestamp % 1000000,
                    "steps": settings["steps"],
                    "cfg": settings["cfg"],
                    "sampler_name": settings["sampler"],
                    "scheduler": "normal",
                    "denoise": 1.0,
                    "model": ["6", 0],
                    "positive": ["1", 0],
                    "negative": ["4", 0],
                    "latent_image": ["3", 0]
                },
                "class_type": "KSampler"
            },
            "6": {
                "inputs": {
                    "unet_name": "Wan2_1-InfiniTetalk-Single_fp16.safetensors",
                    "weight_dtype": "default"
                },
                "class_type": "UNETLoader"
            },
            "7": {
                "inputs": {
                    "samples": ["5", 0],
                    "vae": ["8", 0]
                },
                "class_type": "VAEDecode"
            },
            "8": {
                "inputs": {
                    "vae_name": "Wan2_1_VAE_bf16.safetensors"
                },
                "class_type": "VAELoader"
            },
            "9": {
                "inputs": {
                    "filename_prefix": f"optimized_batch_{timestamp}",
                    "images": ["7", 0]
                },
                "class_type": "SaveImage"
            }
        }
    
    def generate_batch(self, base_prompts: List[str], use_optimization: bool = True):
        """Generate multiple optimized images"""
        comfy_available, ollama_available = self.check_systems()
        
        if not comfy_available:
            print("❌ ComfyUI not available. Cannot generate images.")
            return []
        
        if use_optimization and not ollama_available:
            print("⚠️  Ollama not available. Using fallback optimization.")
        
        print(f"\n🎨 Starting batch generation of {len(base_prompts)} images...")
        print(f"🤖 AI Optimization: {'ENABLED' if use_optimization else 'DISABLED'}")
        
        results = []
        
        for i, base_prompt in enumerate(base_prompts, 1):
            print(f"\n{'='*60}")
            print(f"🎯 [{i}/{len(base_prompts)}] Processing: {base_prompt[:50]}...")
            
            timestamp = int(time.time()) + i
            
            # Optimize prompt if requested
            if use_optimization:
                print("🧠 Optimizing prompt with AI...")
                optimized_data = self.optimizer.optimize_prompt(base_prompt)
                print(f"✨ Style Notes: {optimized_data['style_notes']}")
                print(f"📝 Enhanced Prompt: {optimized_data['optimized_prompt'][:100]}...")
            else:
                optimized_data = self.optimizer.fallback_optimization(base_prompt)
            
            # Create workflow
            workflow = self.create_optimized_workflow(optimized_data, timestamp)
            
            # Save workflow and optimization data
            os.makedirs("workflows/batch", exist_ok=True)
            workflow_file = f"workflows/batch/optimized_{timestamp}.json"
            optimization_file = f"workflows/batch/optimization_{timestamp}.json"
            
            with open(workflow_file, 'w') as f:
                json.dump(workflow, f, indent=2)
            
            with open(optimization_file, 'w') as f:
                json.dump({
                    "original_prompt": base_prompt,
                    "optimization_data": optimized_data,
                    "timestamp": timestamp
                }, f, indent=2)
            
            # Queue generation
            try:
                response = requests.post(f"{self.base_url}/prompt", json={"prompt": workflow})
                if response.status_code == 200:
                    prompt_id = response.json().get("prompt_id")
                    print(f"✅ Queued successfully! ID: {prompt_id}")
                    results.append({
                        "prompt_id": prompt_id,
                        "original_prompt": base_prompt,
                        "optimized_prompt": optimized_data["optimized_prompt"],
                        "workflow_file": workflow_file,
                        "optimization_file": optimization_file,
                        "timestamp": timestamp
                    })
                else:
                    print(f"❌ Queue failed: {response.status_code}")
            except Exception as e:
                print(f"❌ Error queuing: {e}")
            
            # Small delay between requests
            time.sleep(1)
        
        return results

def main():
    print("🚀 Advanced Batch Instagram Generator with AI Optimization")
    print("=" * 65)
    
    generator = AdvancedBatchGenerator()
    
    # High-quality base prompts for Instagram-style content
    instagram_prompts = [
        "gorgeous woman with natural makeup in golden hour lighting",
        "stunning female model with perfect skin and professional photography",
        "elegant influencer in stylish outfit with bokeh background",
        "beautiful portrait of young woman with cinematic lighting",
        "attractive female with radiant smile in modern studio setting",
        "fashionable woman with flowing hair in soft natural light",
        "professional headshot of confident woman with perfect composition",
        "glamorous portrait with dramatic lighting and artistic depth",
        "sophisticated woman in elegant pose with premium photography",
        "captivating female model with flawless makeup and styling"
    ]
    
    print("🎨 Available Instagram Prompts:")
    for i, prompt in enumerate(instagram_prompts, 1):
        print(f"{i:2d}. {prompt}")
    
    print("\n🤖 Options:")
    print("1. Generate ALL with AI optimization (Recommended)")
    print("2. Generate ALL with basic enhancement")
    print("3. Generate first 5 with AI optimization")
    print("4. Custom selection")
    
    try:
        choice = input("\nSelect option (1-4) or press Enter for option 1: ").strip()
        if not choice:
            choice = "1"
        
        if choice == "1":
            selected_prompts = instagram_prompts
            use_ai = True
        elif choice == "2":
            selected_prompts = instagram_prompts
            use_ai = False
        elif choice == "3":
            selected_prompts = instagram_prompts[:5]
            use_ai = True
        elif choice == "4":
            indices = input("Enter prompt numbers (e.g., 1,3,5-7): ").strip()
            # Parse indices (simplified for demo)
            selected_prompts = instagram_prompts[:3]  # Default to first 3
            use_ai = True
        else:
            print("Invalid choice, using option 1")
            selected_prompts = instagram_prompts
            use_ai = True
        
        print(f"\n🎯 Generating {len(selected_prompts)} optimized images...")
        results = generator.generate_batch(selected_prompts, use_ai)
        
        if results:
            print(f"\n🎉 Batch generation completed!")
            print(f"📊 Successfully queued: {len(results)} images")
            print("\n📝 Generation Summary:")
            for i, result in enumerate(results, 1):
                print(f"{i:2d}. ID: {result['prompt_id']}")
                print(f"    Original: {result['original_prompt'][:50]}...")
                print(f"    Optimized: {result['optimized_prompt'][:50]}...")
            
            print(f"\n⏳ Estimated completion time: {len(results) * 2}-{len(results) * 4} minutes")
            print("📁 Check /workspace/ComfyUI/output/ for results")
            print("🌐 Monitor progress at: http://localhost:8188")
        else:
            print("\n❌ No images were queued successfully")
            
    except KeyboardInterrupt:
        print("\n👋 Generation cancelled")
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    main()
