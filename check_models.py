#!/usr/bin/env python3
"""
Check available models in ComfyUI
"""
import requests
import json


def check_available_models():
    """Check what models are available"""
    try:
        # Get object info which includes available models
        response = requests.get("http://localhost:8188/object_info")
        if response.status_code == 200:
            data = response.json()

            # Check for UNet loaders
            if "UNETLoader" in data:
                print("🔧 Available UNet Models:")
                unet_models = data["UNETLoader"]["input"]["required"]["unet_name"][0]
                for model in unet_models:
                    print(f"  - {model}")

            # Check for VAE loaders
            if "VAELoader" in data:
                print("\n🎨 Available VAE Models:")
                vae_models = data["VAELoader"]["input"]["required"]["vae_name"][0]
                for model in vae_models:
                    print(f"  - {model}")

            # Check for CLIP loaders
            if "DualCLIPLoader" in data:
                print("\n📝 Available CLIP Models:")
                clip1_models = data["DualCLIPLoader"]["input"]["required"][
                    "clip_name1"
                ][0]
                clip2_models = data["DualCLIPLoader"]["input"]["required"][
                    "clip_name2"
                ][0]
                print("  CLIP 1:")
                for model in clip1_models[:3]:  # Show first few
                    print(f"    - {model}")
                print("  CLIP 2:")
                for model in clip2_models[:3]:  # Show first few
                    print(f"    - {model}")

            return data
        else:
            print(f"Failed to get model info: {response.status_code}")
            return None

    except Exception as e:
        print(f"Exception: {e}")
        return None


if __name__ == "__main__":
    print("🔍 Checking available ComfyUI models...")
    check_available_models()
