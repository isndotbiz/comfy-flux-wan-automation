#!/usr/bin/env python3
"""
Fixed ComfyUI Test - Complete Flux workflow
"""
import requests
import json


def test_complete_flux_workflow():
    """Test a complete Flux workflow with all necessary nodes"""

    workflow = {
        # Positive prompt encoding
        "1": {
            "inputs": {
                "text": "beautiful woman, professional photography",
                "clip": ["3", 0],
            },
            "class_type": "CLIPTextEncode",
        },
        # Negative prompt encoding
        "2": {
            "inputs": {"text": "blurry, low quality", "clip": ["3", 0]},
            "class_type": "CLIPTextEncode",
        },
        # CLIP loader
        "3": {
            "inputs": {
                "clip_name1": "umt5-xxl-enc-bf16.safetensors",
                "clip_name2": "open-clip-xlm-roberta-large-vit-huge-14_visual_fp16.safetensors",
                "type": "flux",
            },
            "class_type": "DualCLIPLoader",
        },
        # UNet loader
        "4": {
            "inputs": {"unet_name": "flux1-dev.safetensors", "weight_dtype": "default"},
            "class_type": "UNETLoader",
        },
        # Flux guidance
        "5": {
            "inputs": {"guidance": 3.5, "conditioning": ["1", 0]},
            "class_type": "FluxGuidance",
        },
        # Basic guider
        "6": {
            "inputs": {"model": ["4", 0], "conditioning": ["5", 0]},
            "class_type": "BasicGuider",
        },
        # Random noise
        "7": {"inputs": {"noise_seed": 42}, "class_type": "RandomNoise"},
        # Basic scheduler
        "8": {
            "inputs": {
                "model": ["4", 0],
                "scheduler": "simple",
                "steps": 20,
                "denoise": 1.0,
            },
            "class_type": "BasicScheduler",
        },
        # Sampler
        "9": {
            "inputs": {
                "noise": ["7", 0],
                "guider": ["6", 0],
                "sampler": ["10", 0],
                "sigmas": ["8", 0],
                "latent_image": ["11", 0],
            },
            "class_type": "SamplerCustomAdvanced",
        },
        # KSampler select
        "10": {"inputs": {"sampler_name": "euler"}, "class_type": "KSamplerSelect"},
        # Empty latent image
        "11": {
            "inputs": {"width": 1024, "height": 1024, "batch_size": 1},
            "class_type": "EmptyLatentImage",
        },
        # VAE loader
        "12": {"inputs": {"vae_name": "ae.safetensors"}, "class_type": "VAELoader"},
        # VAE decode
        "13": {
            "inputs": {"samples": ["9", 0], "vae": ["12", 0]},
            "class_type": "VAEDecode",
        },
        # Save image (OUTPUT NODE)
        "14": {
            "inputs": {"filename_prefix": "flux_test", "images": ["13", 0]},
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
    print("🧪 Testing complete ComfyUI Flux workflow...")
    result = test_complete_flux_workflow()
    print(f"Result: {result}")
