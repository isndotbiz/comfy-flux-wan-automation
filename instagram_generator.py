#!/usr/bin/env python3
"""
Instagram-Style Image Generator
Direct API integration with ComfyUI for generating Instagram-style images
"""
import json
import time
import requests
import sys
import os
from pathlib import Path

class InstagramGenerator:
    def __init__(self, base_url="http://127.0.0.1:8188"):
        self.base_url = base_url
        self.output_dir = Path("/workspace/ComfyUI/output")
        
    def is_comfyui_running(self):
        """Check if ComfyUI server is running"""
        try:
            response = requests.get(f"{self.base_url}/system_stats", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def create_instagram_workflow(self, prompt, seed=None):
        """Create Instagram-style workflow"""
        if seed is None:
            seed = int(time.time()) % 1000000
            
        timestamp = int(time.time())
        
        workflow = {
            "1": {
                "inputs": {
                    "width": 1024,
                    "height": 1024,
                    "batch_size": 1
                },
                "class_type": "EmptyLatentImage"
            },
            "2": {
                "inputs": {
                    "text": f"{prompt}, professional photography, instagram style, high quality, detailed, cinematic lighting, sharp focus",
                    "clip": ["11", 0]
                },
                "class_type": "CLIPTextEncode"
            },
            "3": {
                "inputs": {
                    "text": "blurry, low quality, distorted, amateur, bad lighting, pixelated, ugly, deformed",
                    "clip": ["11", 0]
                },
                "class_type": "CLIPTextEncode"
            },
            "4": {
                "inputs": {
                    "seed": seed,
                    "steps": 25,
                    "cfg": 7.5,
                    "sampler_name": "euler",
                    "scheduler": "normal",
                    "denoise": 1.0,
                    "model": ["10", 0],
                    "positive": ["2", 0],
                    "negative": ["3", 0],
                    "latent_image": ["1", 0]
                },
                "class_type": "KSampler"
            },
            "5": {
                "inputs": {
                    "samples": ["4", 0],
                    "vae": ["12", 0]
                },
                "class_type": "VAEDecode"
            },
            "6": {
                "inputs": {
                    "filename_prefix": f"instagram_{timestamp}",
                    "images": ["5", 0]
                },
                "class_type": "SaveImage"
            },
            "10": {
                "inputs": {
                    "unet_name": "flux1-dev.safetensors"
                },
                "class_type": "UNETLoader"
            },
            "11": {
                "inputs": {
                    "clip_name1": "t5xxl_fp16.safetensors",
                    "clip_name2": "clip_l.safetensors"
                },
                "class_type": "DualCLIPLoader"
            },
            "12": {
                "inputs": {
                    "vae_name": "ae.safetensors"
                },
                "class_type": "VAELoader"
            }
        }
        
        return workflow, timestamp
    
    def queue_generation(self, workflow):
        """Queue workflow for generation"""
        try:
            data = {"prompt": workflow}
            response = requests.post(f"{self.base_url}/prompt", json=data)
            if response.status_code == 200:
                return response.json().get("prompt_id")
            else:
                print(f"Error queuing: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            print(f"Failed to queue: {e}")
            return None
    
    def generate_instagram_image(self, prompt):
        """Generate Instagram-style image"""
        print(f"🎨 Generating Instagram image...")
        print(f"📝 Prompt: {prompt}")
        
        if not self.is_comfyui_running():
            print("❌ ComfyUI is not running!")
            print("   Start it with: cd /workspace/ComfyUI && python main.py --listen")
            return None
        
        workflow, timestamp = self.create_instagram_workflow(prompt)
        
        # Save workflow for inspection
        workflow_file = f"workflows/instagram_{timestamp}.json"
        os.makedirs("workflows", exist_ok=True)
        with open(workflow_file, 'w') as f:
            json.dump(workflow, f, indent=2)
        
        print(f"💾 Workflow saved: {workflow_file}")
        
        # Queue generation
        prompt_id = self.queue_generation(workflow)
        
        if prompt_id:
            print(f"✅ Queued successfully!")
            print(f"   Prompt ID: {prompt_id}")
            print(f"   Expected output: instagram_{timestamp}_*.png")
            print(f"   Output directory: {self.output_dir}")
            print(f"🌐 Monitor at: http://localhost:8188")
            return prompt_id
        else:
            print("❌ Failed to queue generation")
            return None

def main():
    print("🚀 ComfyUI Instagram Generator")
    print("=" * 40)
    
    generator = InstagramGenerator()
    
    # Instagram-style prompts
    prompts = [
        "beautiful young woman with natural makeup, soft lighting, professional portrait",
        "stunning influencer girl with perfect skin, golden hour lighting, bokeh background", 
        "elegant woman in fashionable outfit, studio photography, high fashion style",
        "attractive female model with flowing hair, cinematic lighting, artistic portrait",
        "gorgeous woman with radiant smile, modern photography, instagram influencer style"
    ]
    
    print("Available prompts:")
    for i, prompt in enumerate(prompts, 1):
        print(f"{i}. {prompt}")
    
    try:
        choice = input("\nSelect prompt number (1-5) or press Enter for #1: ").strip()
        if not choice:
            choice = "1"
        
        idx = int(choice) - 1
        if 0 <= idx < len(prompts):
            selected_prompt = prompts[idx]
        else:
            print("Invalid choice, using prompt #1")
            selected_prompt = prompts[0]
        
        print(f"\n🎯 Selected: {selected_prompt}")
        
        # Generate image
        prompt_id = generator.generate_instagram_image(selected_prompt)
        
        if prompt_id:
            print("\n🎉 Generation started successfully!")
            print("⏳ This may take 1-3 minutes depending on your GPU...")
            print("📁 Check the output directory for results!")
        else:
            print("\n❌ Generation failed!")
            
    except (ValueError, KeyboardInterrupt):
        print("\n👋 Goodbye!")

if __name__ == "__main__":
    main()
