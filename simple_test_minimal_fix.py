#!/usr/bin/env python3
"""
Minimal fix for ComfyUI Test - Just add SaveImage output
"""
import requests
import json


def test_simple_workflow():
    """Test a minimal workflow with output node"""

    workflow = {
        "1": {
            "inputs": {
                "text": "beautiful woman, professional photography",
                "clip": ["3", 0],
            },
            "class_type": "CLIPTextEncode",
        },
        "2": {
            "inputs": {"text": "blurry, low quality", "clip": ["3", 0]},
            "class_type": "CLIPTextEncode",
        },
        "3": {
            "inputs": {
                "clip_name1": "umt5-xxl-enc-bf16.safetensors",
                "clip_name2": "open-clip-xlm-roberta-large-vit-huge-14_visual_fp16.safetensors",
                "type": "flux",
            },
            "class_type": "DualCLIPLoader",
        },
        # Add a dummy image for testing (replace with actual workflow output)
        "4": {
            "inputs": {"width": 512, "height": 512, "batch_size": 1},
            "class_type": "EmptyLatentImage",
        },
        # VAE loader
        "5": {
            "inputs": {"vae_name": "Wan2_1_VAE_bf16.safetensors"},
            "class_type": "VAELoader",
        },
        # VAE decode (dummy)
        "6": {
            "inputs": {"samples": ["4", 0], "vae": ["5", 0]},
            "class_type": "VAEDecode",
        },
        # REQUIRED: Output node
        "7": {
            "inputs": {"filename_prefix": "test_output", "images": ["6", 0]},
            "class_type": "SaveImage",
        },
    }

    try:
        response = requests.post(
            "http://localhost:8188/prompt", json={"prompt": workflow}
        )
        print(f"Response: {response.status_code}")
        if response.status_code != 200:
            print(f"Error: {response.text}")
        else:
            print("Success!")
            return response.json()
    except Exception as e:
        print(f"Exception: {e}")


if __name__ == "__main__":
    print("🧪 Testing minimal ComfyUI workflow with output...")
    result = test_simple_workflow()
    print(f"Result: {result}")
