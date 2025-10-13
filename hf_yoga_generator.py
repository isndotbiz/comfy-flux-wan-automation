#!/usr/bin/env python3
"""
Hugging Face Inference API Yoga Beach Image Generator
Uses HF Inference API for FLUX model generation
Generates 10 high-quality yoga beach images for testing
"""

import sys
import os
import asyncio
import aiohttp
import time
from datetime import datetime
from pathlib import Path
import json
import random
import base64

sys.path.append("./src")
from config import HF_TOKEN, verify_secrets

# Verify secrets are loaded
if not verify_secrets():
    print("❌ HF_TOKEN not found!")
    print("Make sure ~/Workspaces/secrets.env contains HF_TOKEN")
    sys.exit(1)

print(f"✅ Hugging Face token configured: {HF_TOKEN[:10]}...")

# Enhanced prompts optimized for FLUX
BASE_PROMPT = """professional lifestyle photography, beautiful physically fit woman in mid-20s practicing {pose} on pristine summer beach during {lighting}, perfect anatomy, athletic toned physique, yoga athletic wear, serene peaceful expression, clear ocean waves background, white sandy beach, natural lighting, detailed skin textures, high contrast, vibrant warm colors, award winning photography, masterpiece, 8k uhd, sharp focus"""

# 10 yoga poses to test
YOGA_POSES = [
    {
        "name": "warrior_I_sunrise",
        "pose": "Warrior I pose (Virabhadrasana I) with arms raised overhead",
        "lighting": "golden sunrise",
    },
    {
        "name": "warrior_II_sunset",
        "pose": "Warrior II pose (Virabhadrasana II) with arms extended",
        "lighting": "warm sunset glow",
    },
    {
        "name": "warrior_III_midday",
        "pose": "Warrior III pose (Virabhadrasana III) balancing on one leg",
        "lighting": "bright midday sun",
    },
    {
        "name": "tree_pose_morning",
        "pose": "Tree pose (Vrksasana) with hands in prayer position",
        "lighting": "soft morning light",
    },
    {
        "name": "triangle_pose_sunset",
        "pose": "Triangle pose (Trikonasana) with hand on ankle",
        "lighting": "golden sunset",
    },
    {
        "name": "extended_triangle_golden",
        "pose": "Extended Triangle pose (Utthita Trikonasana)",
        "lighting": "golden hour",
    },
    {
        "name": "mountain_pose_sunrise",
        "pose": "Mountain pose (Tadasana) standing tall",
        "lighting": "sunrise glow",
    },
    {
        "name": "standing_forward_fold",
        "pose": "Standing Forward Fold (Uttanasana)",
        "lighting": "soft diffused light",
    },
    {
        "name": "eagle_pose_morning",
        "pose": "Eagle pose (Garudasana) with arms and legs wrapped",
        "lighting": "morning light",
    },
    {
        "name": "goddess_pose_sunset",
        "pose": "Goddess pose (Utkata Konasana) wide-legged squat",
        "lighting": "sunset",
    },
]


async def generate_single_image_hf(session, pose_info, index):
    """Generate a single image using Hugging Face Inference API"""
    try:
        print(f"📸 {index:2d}/10: Generating {pose_info['name']}")

        prompt = BASE_PROMPT.format(
            pose=pose_info["pose"], lighting=pose_info["lighting"]
        )

        # Hugging Face Inference API endpoint for FLUX
        model_id = "black-forest-labs/FLUX.1-schnell"
        url = f"https://api-inference.huggingface.co/models/{model_id}"

        headers = {
            "Authorization": f"Bearer {HF_TOKEN}",
            "Content-Type": "application/json",
        }

        payload = {
            "inputs": prompt,
            "parameters": {
                "num_inference_steps": 4,
                "guidance_scale": 0.0,  # FLUX Schnell uses guidance_scale=0
                "width": 1024,
                "height": 768,
            },
        }

        # Make the API call
        async with session.post(
            url, json=payload, headers=headers, timeout=90
        ) as response:
            if response.status == 200:
                # HF returns image bytes directly
                image_data = await response.read()

                # Save the image
                filename = f"yoga_{pose_info['name']}_{index:03d}.jpg"
                filepath = f"generated_images/{filename}"

                with open(filepath, "wb") as f:
                    f.write(image_data)

                print(f"   ✅ {pose_info['name']} completed! -> {filename}")
                return {
                    "index": index,
                    "name": pose_info["name"],
                    "pose": pose_info["pose"],
                    "status": "success",
                    "filename": filename,
                    "prompt": prompt,
                    "lighting": pose_info["lighting"],
                    "timestamp": datetime.now().isoformat(),
                    "api": "huggingface",
                }

            elif response.status == 503:
                error_text = await response.text()
                if "loading" in error_text.lower():
                    print(
                        f"   ⏳ {pose_info['name']} - Model loading, retrying in 20s..."
                    )
                    await asyncio.sleep(20)
                    # Retry once
                    return await generate_single_image_hf(session, pose_info, index)
                else:
                    print(f"   ❌ {pose_info['name']} failed - Service unavailable")
                    return {
                        "index": index,
                        "name": pose_info["name"],
                        "status": "failed",
                        "error": f"Service unavailable: {error_text[:200]}",
                        "timestamp": datetime.now().isoformat(),
                    }
            else:
                error_text = await response.text()
                print(f"   ❌ {pose_info['name']} failed - HTTP {response.status}")
                return {
                    "index": index,
                    "name": pose_info["name"],
                    "status": "failed",
                    "error": f"HTTP {response.status}: {error_text[:200]}",
                    "timestamp": datetime.now().isoformat(),
                }

    except Exception as e:
        print(f"   ❌ {pose_info['name']} failed - {str(e)[:100]}")
        return {
            "index": index,
            "name": pose_info["name"],
            "status": "failed",
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
        }


async def generate_all_images():
    """Generate all images using Hugging Face API"""
    print("🧘‍♀️ Hugging Face FLUX Yoga Beach Image Generation!")
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🤗 Using Hugging Face Inference API - FLUX.1 Schnell")
    print("=" * 60)

    # Create output directory
    Path("generated_images").mkdir(exist_ok=True)

    start_time = time.time()

    # Create session with timeout
    timeout = aiohttp.ClientTimeout(total=180, connect=30)

    async with aiohttp.ClientSession(timeout=timeout) as session:
        print(f"🚀 Generating {len(YOGA_POSES)} yoga beach images...")
        print()

        # Execute sequentially with delays to avoid rate limits
        results = []
        for i, pose_info in enumerate(YOGA_POSES, 1):
            result = await generate_single_image_hf(session, pose_info, i)
            results.append(result)

            # Add delay between requests to be nice to HF API
            if i < len(YOGA_POSES):
                await asyncio.sleep(5)

    # Analyze results
    successful = [r for r in results if r.get("status") == "success"]
    failed = [r for r in results if r.get("status") == "failed"]

    total_time = time.time() - start_time

    # Save detailed log
    log_data = {
        "generator": "Hugging Face Inference API - FLUX.1 Schnell",
        "timestamp": datetime.now().isoformat(),
        "total_requested": len(YOGA_POSES),
        "successful": len(successful),
        "failed": len(failed),
        "success_rate": len(successful) / len(YOGA_POSES) * 100,
        "total_time_minutes": total_time / 60,
        "average_time_per_image": total_time / len(YOGA_POSES),
        "images": results,
    }

    with open("hf_yoga_generation_log.json", "w") as f:
        json.dump(log_data, f, indent=2)

    # Results summary
    print("\n" + "=" * 60)
    print(f"🎉 Hugging Face Generation Complete!")
    print(
        f"✅ Successfully generated: {len(successful)}/{len(YOGA_POSES)} images ({len(successful)/len(YOGA_POSES)*100:.1f}%)"
    )
    print(f"❌ Failed: {len(failed)}/{len(YOGA_POSES)} images")
    print(f"⏱️  Total time: {total_time/60:.1f} minutes")
    if successful:
        print(
            f"⚡ Average speed: {total_time/len(successful):.1f}s per successful image"
        )
    print(f"📁 Images saved in: ./generated_images/")
    print(f"📝 Detailed log: hf_yoga_generation_log.json")

    if successful:
        print(f"\n🖼️  Generated images:")
        for result in successful:
            print(f"   - {result['filename']}: {result['pose']}")

    return len(successful), len(failed)


if __name__ == "__main__":
    print("🚀 Hugging Face FLUX Yoga Beach Generator")
    print("Testing with 10 yoga poses using HF Inference API!")
    print("=" * 60)

    # Run the generation
    success_count, fail_count = asyncio.run(generate_all_images())

    print(f"\n🏁 Final Results:")
    if success_count >= 8:
        print("🎉 Excellent! Most images generated successfully!")
        print("✨ Ready to scale to full 50 image generation!")
    elif success_count >= 5:
        print("👍 Good results! The API is working well!")
    elif success_count >= 2:
        print("😊 Some success! May need to adjust settings.")
    else:
        print("⚠️  Issues with API. Check the logs for details.")

    print(
        f"📊 Success Rate: {success_count}/{success_count+fail_count} ({success_count/(success_count+fail_count)*100:.1f}%)"
    )

    # If successful, offer to generate more
    if success_count >= 5:
        print("\n🚀 This is working well!")
        print("✨ Ready to create the full 50-image version!")
