#!/usr/bin/env python3
"""
Simple ComfyUI Test - Check what works
"""
import requests
import json

def test_simple_workflow():
    """Test a minimal workflow"""
    
    workflow = {
        "1": {
            "inputs": {
                "text": "beautiful woman, professional photography",
                "clip": ["3", 0]
            },
            "class_type": "CLIPTextEncode"
        },
        "2": {
            "inputs": {
                "text": "blurry, low quality",
                "clip": ["3", 0]
            },
            "class_type": "CLIPTextEncode"
        },
        "3": {
            "inputs": {
                "clip_name1": "umt5-xxl-enc-bf16.safetensors",
                "clip_name2": "open-clip-xlm-roberta-large-vit-huge-14_visual_fp16.safetensors",
                "type": "flux"
            },
            "class_type": "DualCLIPLoader"
        }
    }
    
    try:
        response = requests.post("http://localhost:8188/prompt", json={"prompt": workflow})
        print(f"Response: {response.status_code}")
        if response.status_code != 200:
            print(f"Error: {response.text}")
        else:
            print("Success!")
            return response.json()
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    print("🧪 Testing ComfyUI capabilities...")
    result = test_simple_workflow()
    print(f"Result: {result}")
