#!/usr/bin/env python3
"""
Simple fal.ai HTTP API Yoga Beach Image Generator
Uses direct HTTP requests to bypass client library issues
Generates 50 high-quality yoga beach images
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

sys.path.append("./src")
from config import FAL_API, verify_secrets

# Verify secrets are loaded
if not verify_secrets():
    print("❌ FAL_API key not found!")
    print("Make sure ~/Workspaces/secrets.env contains FAL_API")
    sys.exit(1)

print(f"✅ fal.ai API key configured: {FAL_API[:10]}...")

# Enhanced prompts optimized for FLUX
BASE_PROMPT = """professional lifestyle photography, beautiful physically fit woman in mid-20s practicing {pose} on pristine summer beach during {lighting}, perfect anatomy, athletic toned physique, yoga athletic wear, serene peaceful expression, clear ocean waves background, white sandy beach, natural lighting, detailed skin textures, high contrast, vibrant warm colors, award winning photography, masterpiece, 8k uhd, sharp focus"""

NEGATIVE_PROMPT = "deformed anatomy, distorted limbs, poorly drawn hands, bad anatomy, extra limbs, missing limbs, mutation, ugly, blurry, low quality, cartoon, anime, 3d render, plastic skin"

# First 10 yoga poses to test the system
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


async def generate_single_image_http(session, pose_info, index):
    """Generate a single image using direct HTTP API calls to fal.ai"""
    try:
        print(f"📸 {index:2d}/10: Generating {pose_info['name']}")

        prompt = BASE_PROMPT.format(
            pose=pose_info["pose"], lighting=pose_info["lighting"]
        )

        # fal.ai API endpoint for FLUX Schnell
        url = "https://api.fal.ai/fal-ai/flux/schnell"

        headers = {
            "Authorization": f"Bearer {FAL_API}",
            "Content-Type": "application/json",
        }

        payload = {
            "prompt": prompt,
            "negative_prompt": NEGATIVE_PROMPT,
            "image_size": "landscape_4_3",  # 1024x768
            "num_inference_steps": 4,
            "seed": random.randint(1, 2**32 - 1),
            "enable_safety_checker": True,
        }

        # Make the API call
        async with session.post(
            url, json=payload, headers=headers, timeout=60
        ) as response:
            if response.status == 200:
                result = await response.json()

                if "images" in result and len(result["images"]) > 0:
                    image_url = result["images"][0]["url"]

                    # Download the image
                    async with session.get(image_url) as img_response:
                        if img_response.status == 200:
                            filename = f"yoga_{pose_info['name']}_{index:03d}.jpg"
                            filepath = f"generated_images/{filename}"

                            with open(filepath, "wb") as f:
                                f.write(await img_response.read())

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
                                "url": image_url,
                            }

                print(f"   ❌ {pose_info['name']} failed - No image in response")
                return {
                    "index": index,
                    "name": pose_info["name"],
                    "status": "failed",
                    "error": "No image in response",
                    "response": str(result)[:200],
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
    """Generate all images using direct HTTP calls"""
    print("🧘‍♀️ fal.ai HTTP API Yoga Beach Image Generation!")
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🟦 Using fal.ai FLUX.1 [schnell] via HTTP API")
    print("=" * 60)

    # Create output directory
    Path("generated_images").mkdir(exist_ok=True)

    start_time = time.time()

    # Create session with timeout and connection limits
    timeout = aiohttp.ClientTimeout(total=120, connect=30)
    connector = aiohttp.TCPConnector(limit=3, limit_per_host=3)  # Rate limiting

    async with aiohttp.ClientSession(timeout=timeout, connector=connector) as session:
        # Create tasks with rate limiting
        tasks = []
        for i, pose_info in enumerate(YOGA_POSES, 1):
            task = generate_single_image_http(session, pose_info, i)
            tasks.append(task)

        print(f"🚀 Launching {len(tasks)} generation tasks...")
        print()

        # Execute with some delay between starts
        results = []
        for i, task in enumerate(tasks):
            if i > 0:  # Add delay between requests
                await asyncio.sleep(2)
            result = await task
            results.append(result)

    # Analyze results
    successful = [r for r in results if r.get("status") == "success"]
    failed = [r for r in results if r.get("status") == "failed"]

    total_time = time.time() - start_time

    # Save detailed log
    log_data = {
        "generator": "fal.ai HTTP API - FLUX.1 schnell",
        "timestamp": datetime.now().isoformat(),
        "total_requested": len(YOGA_POSES),
        "successful": len(successful),
        "failed": len(failed),
        "success_rate": len(successful) / len(YOGA_POSES) * 100,
        "total_time_minutes": total_time / 60,
        "average_time_per_image": total_time / len(YOGA_POSES),
        "images": results,
    }

    with open("simple_fal_generation_log.json", "w") as f:
        json.dump(log_data, f, indent=2)

    # Results summary
    print("\n" + "=" * 60)
    print(f"🎉 fal.ai HTTP Generation Complete!")
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
    print(f"📝 Detailed log: simple_fal_generation_log.json")

    if successful:
        print(f"\n🖼️  Generated images:")
        for result in successful:
            print(f"   - {result['filename']}: {result['pose']}")

    return len(successful), len(failed)


if __name__ == "__main__":
    print("🚀 Simple fal.ai HTTP API Yoga Beach Generator")
    print("Testing with 10 yoga poses using direct API calls!")
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
