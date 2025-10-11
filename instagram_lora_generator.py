#!/usr/bin/env python3
"""
Instagram Model Generator with LoRA Support
Enhanced version with Flux.1 LoRA integration for model photography
"""
import json
import time
import requests
import sys
import os
from pathlib import Path
import uuid

class InstagramLoRAGenerator:
    def __init__(self, base_url="http://127.0.0.1:8188"):
        self.base_url = base_url
        self.output_dir = Path("/workspace/ComfyUI/output")
        self.lora_path = "flux_v2_lora_2144476.safetensors"
        
        # Optimized prompts for different styles
        self.prompts = [
            "beautiful young woman, Instagram model portrait, soft golden hour lighting, natural makeup, flowing hair, confident expression, professional photography, shallow depth of field, 85mm lens, warm color grading, high resolution, detailed facial features",
            "stunning young woman, fashion model pose, contemporary style, perfect lighting setup, elegant posture, modern Instagram aesthetic, professional fashion photography, crisp details, natural beauty, commercial quality, clean background",
            "beautiful young woman, lifestyle photography, candid pose, natural sunlight, Instagram influencer style, authentic expression, contemporary fashion, soft shadows, high-end photography, photorealistic, detailed skin texture",
            "gorgeous young woman, glamour photography, professional lighting, Instagram model aesthetic, flawless makeup, elegant pose, high fashion style, studio quality, detailed portrait, commercial photography standards"
        ]
        
    def is_comfyui_running(self):
        """Check if ComfyUI server is running"""
        try:
            response = requests.get(f"{self.base_url}/system_stats", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def create_flux_lora_workflow(self, prompt, seed=None, width=1024, height=1024):
        """Create Flux.1 workflow with LoRA support"""
        if seed is None:
            seed = int(time.time()) % 1000000
            
        workflow = {
            # Load Flux.1 model
            "4": {
                "inputs": {
                    "ckpt_name": "flux1-dev-fp8.safetensors"
                },
                "class_type": "CheckpointLoaderSimple"
            },
            
            # Load LoRA
            "12": {
                "inputs": {
                    "lora_name": self.lora_path,
                    "strength_model": 0.8,
                    "strength_clip": 0.8,
                    "model": ["4", 0],
                    "clip": ["4", 1]
                },
                "class_type": "LoraLoader"
            },
            
            # Positive prompt
            "6": {
                "inputs": {
                    "text": prompt,
                    "clip": ["12", 1]
                },
                "class_type": "CLIPTextEncode"
            },
            
            # Negative prompt
            "7": {
                "inputs": {
                    "text": "blurry, low quality, distorted, amateur, bad lighting, pixelated, ugly, deformed, nsfw",
                    "clip": ["12", 1]
                },
                "class_type": "CLIPTextEncode"
            },
            
            # Empty latent
            "5": {
                "inputs": {
                    "width": width,
                    "height": height,
                    "batch_size": 1
                },
                "class_type": "EmptyLatentImage"
            },
            
            # Flux sampler
            "3": {
                "inputs": {
                    "seed": seed,
                    "steps": 20,
                    "cfg": 1.0,
                    "sampler_name": "euler",
                    "scheduler": "simple",
                    "denoise": 1,
                    "model": ["12", 0],
                    "positive": ["6", 0],
                    "negative": ["7", 0],
                    "latent_image": ["5", 0]
                },
                "class_type": "KSampler"
            },
            
            # VAE decode
            "8": {
                "inputs": {
                    "samples": ["3", 0],
                    "vae": ["4", 2]
                },
                "class_type": "VAEDecode"
            },
            
            # Save image
            "9": {
                "inputs": {
                    "filename_prefix": f"instagram_model_{int(time.time())}",
                    "images": ["8", 0]
                },
                "class_type": "SaveImage"
            }
        }
        
        return workflow
    
    def queue_prompt(self, workflow):
        """Queue a prompt for generation"""
        data = {"prompt": workflow, "client_id": str(uuid.uuid4())}
        
        try:
            response = requests.post(f"{self.base_url}/prompt", json=data)
            if response.status_code == 200:
                result = response.json()
                return result.get('prompt_id')
            else:
                print(f"Error queuing prompt: {response.status_code}")
                return None
        except Exception as e:
            print(f"Error: {e}")
            return None
    
    def check_progress(self, prompt_id):
        """Check the progress of a generation"""
        try:
            response = requests.get(f"{self.base_url}/history/{prompt_id}")
            if response.status_code == 200:
                history = response.json()
                return prompt_id in history
            return False
        except:
            return False
    
    def wait_for_completion(self, prompt_id, timeout=300):
        """Wait for generation to complete"""
        start_time = time.time()
        print(f"⏳ Waiting for image generation (Prompt ID: {prompt_id})")
        
        while time.time() - start_time < timeout:
            if self.check_progress(prompt_id):
                print("✅ Generation completed!")
                return True
            print(".", end="", flush=True)
            time.sleep(2)
        
        print(f"\n❌ Timeout after {timeout} seconds")
        return False
    
    def generate_instagram_batch(self, count=4):
        """Generate a batch of Instagram model images"""
        if not self.is_comfyui_running():
            print("❌ ComfyUI is not running. Please start it first.")
            return False
        
        print(f"🎨 Starting Instagram model generation with LoRA")
        print(f"📁 Using LoRA: {self.lora_path}")
        print(f"🖼️  Generating {count} variations")
        
        generated_ids = []
        
        for i in range(count):
            prompt = self.prompts[i % len(self.prompts)]
            print(f"\n🖼️  Generating variation {i+1}/{count}")
            print(f"📝 Prompt: {prompt[:80]}...")
            
            # Create workflow
            workflow = self.create_flux_lora_workflow(
                prompt=prompt,
                seed=None,  # Random seed for each
                width=1024,
                height=1024
            )
            
            # Queue the prompt
            prompt_id = self.queue_prompt(workflow)
            if prompt_id:
                generated_ids.append(prompt_id)
                print(f"✅ Queued: {prompt_id}")
                
                # Wait for completion
                if self.wait_for_completion(prompt_id):
                    print(f"✅ Variation {i+1} completed")
                else:
                    print(f"❌ Variation {i+1} failed or timed out")
                    
                time.sleep(1)  # Small delay between generations
            else:
                print(f"❌ Failed to queue variation {i+1}")
        
        print(f"\n🎉 Batch generation completed!")
        print(f"📁 Check outputs in: {self.output_dir}")
        
        return generated_ids

def main():
    generator = InstagramLoRAGenerator()
    
    print("🎨 Instagram Model Generator with Flux.1 LoRA")
    print("=" * 50)
    
    # Generate batch of images
    result = generator.generate_instagram_batch(count=4)
    
    if result:
        print(f"\n✅ Successfully generated {len(result)} images")
    else:
        print("\n❌ Generation failed")

if __name__ == "__main__":
    main()
