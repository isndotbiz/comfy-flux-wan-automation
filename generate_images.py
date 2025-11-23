#!/usr/bin/env python3
"""
Generate Images with ComfyUI Flux Workflow
"""
import requests
import json
import time


def generate_image(
    prompt, negative_prompt="blurry, low quality", filename_prefix="flux_generated"
):
    """Generate an image using Flux workflow"""

    workflow = {
        # Positive prompt encoding
        "1": {
            "inputs": {"text": prompt, "clip": ["3", 0]},
            "class_type": "CLIPTextEncode",
        },
        # Negative prompt encoding
        "2": {
            "inputs": {"text": negative_prompt, "clip": ["3", 0]},
            "class_type": "CLIPTextEncode",
        },
        # CLIP loader (using known working models)
        "3": {
            "inputs": {
                "clip_name1": "umt5-xxl-enc-bf16.safetensors",
                "clip_name2": "open-clip-xlm-roberta-large-vit-huge-14_visual_fp16.safetensors",
                "type": "flux",
            },
            "class_type": "DualCLIPLoader",
        },
        # UNet loader - try common Flux model names
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
        # Random noise with varying seed
        "7": {
            "inputs": {"noise_seed": int(time.time()) % 1000000},  # Random seed
            "class_type": "RandomNoise",
        },
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
        # KSampler select
        "9": {"inputs": {"sampler_name": "euler"}, "class_type": "KSamplerSelect"},
        # Sampler
        "10": {
            "inputs": {
                "noise": ["7", 0],
                "guider": ["6", 0],
                "sampler": ["9", 0],
                "sigmas": ["8", 0],
                "latent_image": ["11", 0],
            },
            "class_type": "SamplerCustomAdvanced",
        },
        # Empty latent image
        "11": {
            "inputs": {"width": 1024, "height": 1024, "batch_size": 1},
            "class_type": "EmptyLatentImage",
        },
        # VAE loader (using known working model)
        "12": {
            "inputs": {"vae_name": "Wan2_1_VAE_bf16.safetensors"},
            "class_type": "VAELoader",
        },
        # VAE decode
        "13": {
            "inputs": {"samples": ["10", 0], "vae": ["12", 0]},
            "class_type": "VAEDecode",
        },
        # Save image (OUTPUT NODE)
        "14": {
            "inputs": {"filename_prefix": filename_prefix, "images": ["13", 0]},
            "class_type": "SaveImage",
        },
    }

    try:
        print(f"🎨 Generating image with prompt: '{prompt}'")
        response = requests.post(
            "http://localhost:8188/prompt", json={"prompt": workflow}
        )

        if response.status_code == 200:
            result = response.json()
            prompt_id = result.get("prompt_id")
            print(f"✅ Image generation started! Prompt ID: {prompt_id}")
            return result
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
            return None

    except Exception as e:
        print(f"❌ Exception: {e}")
        return None


def generate_multiple_images():
    """Generate multiple images with different prompts"""

    prompts = [
        "a beautiful landscape with mountains and a lake at sunset, highly detailed, 4k",
        "a cute cat wearing a wizard hat, digital art, fantasy style",
        "a cyberpunk city at night with neon lights, futuristic architecture",
        "a bowl of fresh fruit on a wooden table, natural lighting, photorealistic",
        "an astronaut floating in space with Earth in the background, realistic",
    ]

    results = []

    for i, prompt in enumerate(prompts):
        print(f"\n--- Image {i+1}/5 ---")
        filename = f"generated_image_{i+1:02d}"
        result = generate_image(prompt, filename_prefix=filename)

        if result:
            results.append(result)
            print(f"⏳ Waiting 3 seconds before next generation...")
            time.sleep(3)
        else:
            print(f"⚠️  Failed to generate image {i+1}")

    return results


if __name__ == "__main__":
    print("🖼️  Starting image generation with ComfyUI...")
    results = generate_multiple_images()
    print(f"\n✨ Generation complete! {len(results)} images queued for processing.")
