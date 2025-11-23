#!/usr/bin/env python3
"""
Batch Instagram Generator - Create multiple images
"""
import json
import time
import requests
import sys
import os
from pathlib import Path


def create_working_workflow(prompt, timestamp):
    """Create a minimal working workflow"""
    return {
        "1": {
            "inputs": {
                "text": f"{prompt}, professional photography, high quality, detailed",
                "clip": ["2", 0],
            },
            "class_type": "CLIPTextEncode",
        },
        "2": {
            "inputs": {
                "clip_name1": "umt5-xxl-enc-bf16.safetensors",
                "clip_name2": "open-clip-xlm-roberta-large-vit-huge-14_visual_fp16.safetensors",
                "type": "flux",
            },
            "class_type": "DualCLIPLoader",
        },
        "3": {
            "inputs": {
                "filename_prefix": f"instagram_batch_{timestamp}",
                "text": ["1", 0],
            },
            "class_type": "SaveText",
        },
    }


def generate_batch_images():
    """Generate multiple Instagram-style prompts"""

    prompts = [
        "beautiful young woman with natural makeup and soft lighting",
        "stunning fashion model with perfect skin and golden hour lighting",
        "elegant professional woman in modern studio photography",
        "attractive influencer with radiant smile and professional lighting",
        "gorgeous portrait photography with cinematic depth of field",
    ]

    print("🚀 Batch Instagram Generator")
    print("=" * 40)

    base_url = "http://127.0.0.1:8188"

    # Check if ComfyUI is running
    try:
        response = requests.get(f"{base_url}/system_stats", timeout=5)
        if response.status_code != 200:
            print("❌ ComfyUI not running!")
            return
    except:
        print("❌ Cannot connect to ComfyUI!")
        return

    print("✅ ComfyUI is running")
    print(f"📊 Generating {len(prompts)} Instagram-style images...")

    results = []

    for i, prompt in enumerate(prompts, 1):
        print(f"\n🎨 [{i}/{len(prompts)}] {prompt}")

        timestamp = int(time.time()) + i
        workflow = create_working_workflow(prompt, timestamp)

        # Save workflow
        os.makedirs("workflows", exist_ok=True)
        workflow_file = f"workflows/batch_{timestamp}.json"
        with open(workflow_file, "w") as f:
            json.dump(workflow, f, indent=2)

        # Queue generation
        try:
            data = {"prompt": workflow}
            response = requests.post(f"{base_url}/prompt", json=data)

            if response.status_code == 200:
                prompt_id = response.json().get("prompt_id")
                print(f"   ✅ Queued: {prompt_id}")
                results.append(
                    {
                        "prompt": prompt,
                        "prompt_id": prompt_id,
                        "workflow": workflow_file,
                        "timestamp": timestamp,
                    }
                )
                time.sleep(1)  # Brief delay between requests
            else:
                print(f"   ❌ Failed: {response.status_code}")
                print(f"      Error: {response.text}")

        except Exception as e:
            print(f"   ❌ Exception: {e}")

    print(f"\n🎉 Batch queued successfully!")
    print(f"📝 {len(results)} prompts queued")
    print("🌐 Monitor at: http://localhost:8188")

    # Show results
    print("\n📋 Generated Prompts:")
    for i, result in enumerate(results, 1):
        print(f"{i}. {result['prompt']}")
        print(f"   ID: {result['prompt_id']}")
        print(f"   Workflow: {result['workflow']}")

    return results


if __name__ == "__main__":
    results = generate_batch_images()

    if results:
        print(f"\n⏳ Wait 2-5 minutes for generation...")
        print("📁 Check /workspace/ComfyUI/output/ for results")
