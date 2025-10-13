#!/usr/bin/env python3

import requests
import json
import time
import os
import random

# ComfyUI API endpoint
COMFYUI_URL = "http://localhost:8188"

# Our LoRAs to test
LORAS = [
    "flux_woman_lora.safetensors",
    "lora_1078264.safetensors",
    "lora_1719784.safetensors",
    "lora_2300332.safetensors",
    "lora_733658.safetensors",
    "lora_750209.safetensors",
    "lora_912251.safetensors",
]


def create_flux_workflow(lora_name, seed, image_name):
    """Create a FLUX workflow with LoRA"""
    workflow = {
        "3": {
            "inputs": {
                "seed": seed,
                "steps": 25,
                "cfg": 1.0,
                "sampler_name": "euler",
                "scheduler": "simple",
                "denoise": 1,
                "model": ["12", 0],
                "positive": ["6", 0],
                "negative": ["7", 0],
                "latent_image": ["5", 0],
            },
            "class_type": "KSampler",
        },
        "4": {
            "inputs": {"unet_name": "flux1-dev.safetensors", "weight_dtype": "default"},
            "class_type": "UNETLoader",
        },
        "5": {
            "inputs": {"width": 1024, "height": 1024, "batch_size": 1},
            "class_type": "EmptyLatentImage",
        },
        "6": {
            "inputs": {
                "text": "beautiful late 20s woman, professional portrait, soft lighting, detailed facial features, elegant, photorealistic",
                "clip": ["11", 0],
            },
            "class_type": "CLIPTextEncode",
        },
        "7": {
            "inputs": {
                "text": "blurry, low quality, distorted, bad anatomy",
                "clip": ["11", 0],
            },
            "class_type": "CLIPTextEncode",
        },
        "8": {
            "inputs": {"samples": ["3", 0], "vae": ["9", 0]},
            "class_type": "VAEDecode",
        },
        "9": {"inputs": {"vae_name": "ae.safetensors"}, "class_type": "VAELoader"},
        "10": {
            "inputs": {"filename_prefix": image_name, "images": ["8", 0]},
            "class_type": "SaveImage",
        },
        "11": {
            "inputs": {
                "clip_name1": "clip_l.safetensors",
                "clip_name2": "umt5_xxl_fp8_e4m3fn_scaled.safetensors",
                "type": "flux",
            },
            "class_type": "DualCLIPLoader",
        },
        "12": {
            "inputs": {
                "model": ["4", 0],
                "clip": ["11", 0],
                "lora_name": lora_name,
                "strength_model": 0.8,
                "strength_clip": 0.8,
            },
            "class_type": "LoraLoader",
        },
    }
    return workflow


def queue_workflow(workflow):
    """Queue a workflow in ComfyUI"""
    data = {"prompt": workflow}
    response = requests.post(f"{COMFYUI_URL}/prompt", json=data)
    if response.status_code == 200:
        return response.json()["prompt_id"]
    else:
        print(f"Error queuing workflow: {response.status_code} - {response.text}")
        return None


def wait_for_completion(prompt_id):
    """Wait for workflow completion"""
    while True:
        try:
            response = requests.get(f"{COMFYUI_URL}/history/{prompt_id}")
            if response.status_code == 200:
                history = response.json()
                if prompt_id in history:
                    return True
            time.sleep(2)
        except:
            time.sleep(2)
            continue


def generate_images():
    """Generate 2 images for each LoRA"""
    print("🚀 Starting FLUX + LoRA image generation...")
    print(f"Output directory: /workspace/ComfyUI/output/")

    total_images = 0

    for i, lora in enumerate(LORAS, 1):
        print(f"\n📸 Generating images with LoRA {i}/{len(LORAS)}: {lora}")

        for j in range(1, 3):  # Generate 2 images per LoRA
            seed = random.randint(1, 1000000)
            image_name = f"{lora.replace('.safetensors', '')}_image_{j}"

            print(f"  • Image {j}/2 - Seed: {seed}")

            workflow = create_flux_workflow(lora, seed, image_name)
            prompt_id = queue_workflow(workflow)

            if prompt_id:
                print(f"    Queued with ID: {prompt_id}")
                wait_for_completion(prompt_id)
                print(f"    ✅ Completed!")
                total_images += 1
            else:
                print(f"    ❌ Failed to queue")

        # Small delay between LoRAs
        time.sleep(2)

    print(f"\n🎉 Generation complete! Created {total_images} images total.")
    print(f"📁 All images saved to: /workspace/ComfyUI/output/")

    # List generated files
    output_dir = "/workspace/ComfyUI/output"
    if os.path.exists(output_dir):
        files = [f for f in os.listdir(output_dir) if f.endswith(".png")]
        print(f"\n📋 Generated files ({len(files)}):")
        for file in sorted(files):
            print(f"   • {file}")


if __name__ == "__main__":
    # Check if ComfyUI is running
    try:
        response = requests.get(f"{COMFYUI_URL}/system_stats")
        if response.status_code != 200:
            print("❌ ComfyUI is not running! Please start ComfyUI first.")
            exit(1)
    except:
        print("❌ Cannot connect to ComfyUI! Please start ComfyUI first.")
        exit(1)

    generate_images()
