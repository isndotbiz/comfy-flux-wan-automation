#!/usr/bin/env python3
import argparse
import json
import requests
import time
import uuid


def get_status():
    try:
        response = requests.get("http://localhost:8188/system_stats")
        return response.json() if response.status_code == 200 else None
    except:
        return None


def generate_image(prompt, width=1024, height=1024):
    workflow = {
        "1": {
            "inputs": {"width": width, "height": height, "batch_size": 1},
            "class_type": "EmptyLatentImage",
        },
        "2": {
            "inputs": {"text": prompt, "clip": ["11", 0]},
            "class_type": "CLIPTextEncode",
        },
        "3": {
            "inputs": {"text": "blurry, low quality", "clip": ["11", 0]},
            "class_type": "CLIPTextEncode",
        },
        "4": {
            "inputs": {
                "seed": int(time.time()),
                "steps": 20,
                "cfg": 7.0,
                "sampler_name": "euler",
                "scheduler": "normal",
                "denoise": 1.0,
                "model": ["10", 0],
                "positive": ["2", 0],
                "negative": ["3", 0],
                "latent_image": ["1", 0],
            },
            "class_type": "KSampler",
        },
        "5": {
            "inputs": {"samples": ["4", 0], "vae": ["12", 0]},
            "class_type": "VAEDecode",
        },
        "6": {
            "inputs": {
                "filename_prefix": f"instagram_{int(time.time())}",
                "images": ["5", 0],
            },
            "class_type": "SaveImage",
        },
        "10": {
            "inputs": {"unet_name": "flux1-dev.safetensors"},
            "class_type": "UNETLoader",
        },
        "11": {
            "inputs": {
                "clip_name1": "t5xxl_fp16.safetensors",
                "clip_name2": "clip_l.safetensors",
            },
            "class_type": "DualCLIPLoader",
        },
        "12": {"inputs": {"vae_name": "ae.safetensors"}, "class_type": "VAELoader"},
    }

    try:
        prompt_id = str(uuid.uuid4())
        data = {"prompt": workflow, "client_id": prompt_id}
        response = requests.post("http://localhost:8188/prompt", json=data)
        return response.json().get("prompt_id") if response.status_code == 200 else None
    except Exception as e:
        print(f"Error: {e}")
        return None


def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("status")
    gen_parser = subparsers.add_parser("generate")
    gen_parser.add_argument("prompt")
    gen_parser.add_argument("--width", type=int, default=1024)
    gen_parser.add_argument("--height", type=int, default=1024)

    args = parser.parse_args()

    if args.command == "status":
        status = get_status()
        if status:
            print("✅ ComfyUI Status:")
            print(f"   Version: {status['system']['comfyui_version']}")
            vram_free = status["devices"][0]["vram_free"] / 1024**3
            print(f"   VRAM Free: {vram_free:.1f}GB")
        else:
            print("❌ ComfyUI server not running")

    elif args.command == "generate":
        print(f"🎨 Generating: {args.prompt}")
        prompt_id = generate_image(args.prompt, args.width, args.height)
        if prompt_id:
            print(f"🚀 Queued with ID: {prompt_id}")
            print("🌐 Check progress: http://localhost:8188")
        else:
            print("❌ Failed to queue")


if __name__ == "__main__":
    main()
