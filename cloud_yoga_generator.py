#!/usr/bin/env python3
"""
Multi-API Cloud Yoga Beach Image Generator
Uses fal.ai, Replicate, and Hugging Face APIs for distributed generation
Generates 50 high-quality yoga beach images across multiple providers
"""

import sys
import os
import asyncio
import aiohttp
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
from datetime import datetime
from pathlib import Path
import json
import random

sys.path.append("./src")
from config import FAL_API, REPLICATE_API, HF_TOKEN, verify_secrets

# Verify secrets are loaded
if not verify_secrets():
    print("❌ Required API keys not found!")
    print("Make sure ~/Workspaces/secrets.env contains:")
    print("- FAL_API")
    print("- REPLICATE_API")
    print("- HF_TOKEN")
    sys.exit(1)

# Import API clients
try:
    import fal_client
    import replicate
    from gradio_client import Client, handle_file

    print("✅ All API clients imported successfully")
except ImportError as e:
    print(f"❌ Missing API client: {e}")
    sys.exit(1)

# Configure API clients
fal_client.config(key=FAL_API)
replicate_client = replicate.Client(api_token=REPLICATE_API)

# Enhanced prompts optimized for different APIs
BASE_PROMPTS = {
    "fal": "professional lifestyle photography, beautiful physically fit woman in mid-20s practicing {pose} on pristine summer beach during {lighting}, perfect anatomy, athletic toned physique, yoga athletic wear, serene peaceful expression, clear ocean waves background, white sandy beach, natural lighting, detailed skin textures, high contrast, vibrant warm colors, award winning photography, masterpiece, 8k uhd, sharp focus",
    "replicate": "high quality professional photo of fit young woman doing {pose} yoga pose on beautiful beach at {lighting}, athletic body, yoga outfit, peaceful expression, ocean background, sandy beach, natural lighting, photorealistic, detailed, sharp, 8k",
    "huggingface": "stunning beach yoga photography, fit woman practicing {pose} during {lighting}, athletic physique, yoga clothes, serene expression, ocean waves, sandy beach, professional lighting, high resolution, masterpiece",
}

NEGATIVE_PROMPT = "deformed anatomy, distorted limbs, poorly drawn hands, bad anatomy, extra limbs, missing limbs, mutation, ugly, blurry, low quality, cartoon, anime, 3d render"

# 50 Diverse Yoga poses distributed across APIs
YOGA_POSES = [
    # fal.ai - FLUX.1 model (20 poses)
    {
        "api": "fal",
        "model": "fal-ai/flux/schnell",
        "name": "warrior_I_sunrise",
        "pose": "Warrior I pose (Virabhadrasana I) with arms raised overhead",
        "lighting": "golden sunrise",
    },
    {
        "api": "fal",
        "model": "fal-ai/flux/schnell",
        "name": "warrior_II_sunset",
        "pose": "Warrior II pose (Virabhadrasana II) with arms extended",
        "lighting": "warm sunset glow",
    },
    {
        "api": "fal",
        "model": "fal-ai/flux/schnell",
        "name": "warrior_III_midday",
        "pose": "Warrior III pose (Virabhadrasana III) balancing on one leg",
        "lighting": "bright midday sun",
    },
    {
        "api": "fal",
        "model": "fal-ai/flux/schnell",
        "name": "tree_pose_morning",
        "pose": "Tree pose (Vrksasana) with hands in prayer position",
        "lighting": "soft morning light",
    },
    {
        "api": "fal",
        "model": "fal-ai/flux/schnell",
        "name": "triangle_pose_sunset",
        "pose": "Triangle pose (Trikonasana) with hand on ankle",
        "lighting": "golden sunset",
    },
    {
        "api": "fal",
        "model": "fal-ai/flux/schnell",
        "name": "extended_triangle_golden",
        "pose": "Extended Triangle pose (Utthita Trikonasana)",
        "lighting": "golden hour",
    },
    {
        "api": "fal",
        "model": "fal-ai/flux/schnell",
        "name": "mountain_pose_sunrise",
        "pose": "Mountain pose (Tadasana) standing tall",
        "lighting": "sunrise glow",
    },
    {
        "api": "fal",
        "model": "fal-ai/flux/schnell",
        "name": "standing_forward_fold",
        "pose": "Standing Forward Fold (Uttanasana)",
        "lighting": "soft diffused light",
    },
    {
        "api": "fal",
        "model": "fal-ai/flux/schnell",
        "name": "eagle_pose_morning",
        "pose": "Eagle pose (Garudasana) with arms and legs wrapped",
        "lighting": "morning light",
    },
    {
        "api": "fal",
        "model": "fal-ai/flux/schnell",
        "name": "goddess_pose_sunset",
        "pose": "Goddess pose (Utkata Konasana) wide-legged squat",
        "lighting": "sunset",
    },
    {
        "api": "fal",
        "model": "fal-ai/flux/schnell",
        "name": "chair_pose_midday",
        "pose": "Chair pose (Utkatasana) with arms raised",
        "lighting": "bright sun",
    },
    {
        "api": "fal",
        "model": "fal-ai/flux/schnell",
        "name": "revolved_triangle_golden",
        "pose": "Revolved Triangle pose with spinal twist",
        "lighting": "golden hour",
    },
    {
        "api": "fal",
        "model": "fal-ai/flux/schnell",
        "name": "high_lunge_sunrise",
        "pose": "High Lunge pose with arms overhead",
        "lighting": "sunrise",
    },
    {
        "api": "fal",
        "model": "fal-ai/flux/schnell",
        "name": "crescent_lunge_natural",
        "pose": "Crescent Lunge pose",
        "lighting": "natural daylight",
    },
    {
        "api": "fal",
        "model": "fal-ai/flux/schnell",
        "name": "star_pose_sunset",
        "pose": "Star pose (Utthita Tadasana) with arms and legs wide",
        "lighting": "sunset glow",
    },
    {
        "api": "fal",
        "model": "fal-ai/flux/schnell",
        "name": "lotus_pose_morning",
        "pose": "Lotus pose (Padmasana) meditation position",
        "lighting": "soft morning",
    },
    {
        "api": "fal",
        "model": "fal-ai/flux/schnell",
        "name": "seated_forward_fold",
        "pose": "Seated Forward Fold (Paschimottanasana)",
        "lighting": "natural light",
    },
    {
        "api": "fal",
        "model": "fal-ai/flux/schnell",
        "name": "bound_angle_pose",
        "pose": "Bound Angle pose (Baddha Konasana) butterfly position",
        "lighting": "golden hour",
    },
    {
        "api": "fal",
        "model": "fal-ai/flux/schnell",
        "name": "seated_twist_right",
        "pose": "Seated Spinal Twist (Ardha Matsyendrasana)",
        "lighting": "sunset",
    },
    {
        "api": "fal",
        "model": "fal-ai/flux/schnell",
        "name": "hero_pose_sunset",
        "pose": "Hero pose (Virasana) kneeling meditation",
        "lighting": "sunset",
    },
    # Replicate - FLUX.1-dev (15 poses)
    {
        "api": "replicate",
        "model": "black-forest-labs/flux-dev",
        "name": "sage_pose_morning",
        "pose": "Sage pose (Marichyasana) with arm bind",
        "lighting": "morning",
    },
    {
        "api": "replicate",
        "model": "black-forest-labs/flux-dev",
        "name": "easy_pose_midday",
        "pose": "Easy pose (Sukhasana) cross-legged",
        "lighting": "bright daylight",
    },
    {
        "api": "replicate",
        "model": "black-forest-labs/flux-dev",
        "name": "compass_pose_advanced",
        "pose": "Compass pose (Parivrtta Surya Yantrasana)",
        "lighting": "natural",
    },
    {
        "api": "replicate",
        "model": "black-forest-labs/flux-dev",
        "name": "seated_wide_leg_fold",
        "pose": "Seated Wide-Legged Forward Fold",
        "lighting": "soft light",
    },
    {
        "api": "replicate",
        "model": "black-forest-labs/flux-dev",
        "name": "boat_pose_sunset",
        "pose": "Boat pose (Navasana) core strengthening",
        "lighting": "sunset",
    },
    {
        "api": "replicate",
        "model": "black-forest-labs/flux-dev",
        "name": "crow_pose_morning",
        "pose": "Crow pose (Bakasana) arm balance",
        "lighting": "morning light",
    },
    {
        "api": "replicate",
        "model": "black-forest-labs/flux-dev",
        "name": "side_crow_sunset",
        "pose": "Side Crow pose advanced arm balance",
        "lighting": "sunset",
    },
    {
        "api": "replicate",
        "model": "black-forest-labs/flux-dev",
        "name": "dancers_pose_sunrise",
        "pose": "Dancer's pose (Natarajasana) standing backbend",
        "lighting": "sunrise",
    },
    {
        "api": "replicate",
        "model": "black-forest-labs/flux-dev",
        "name": "standing_hand_to_toe",
        "pose": "Standing Hand-to-Big-Toe pose",
        "lighting": "natural",
    },
    {
        "api": "replicate",
        "model": "black-forest-labs/flux-dev",
        "name": "eight_angle_pose",
        "pose": "Eight-Angle pose (Astavakrasana) advanced twist",
        "lighting": "golden hour",
    },
    {
        "api": "replicate",
        "model": "black-forest-labs/flux-dev",
        "name": "firefly_pose_challenging",
        "pose": "Firefly pose (Tittibhasana) arm balance",
        "lighting": "midday",
    },
    {
        "api": "replicate",
        "model": "black-forest-labs/flux-dev",
        "name": "side_plank_sunset",
        "pose": "Side Plank pose (Vasisthasana)",
        "lighting": "sunset",
    },
    {
        "api": "replicate",
        "model": "black-forest-labs/flux-dev",
        "name": "flying_pigeon_advanced",
        "pose": "Flying Pigeon pose arm balance",
        "lighting": "morning",
    },
    {
        "api": "replicate",
        "model": "black-forest-labs/flux-dev",
        "name": "scale_pose_strength",
        "pose": "Scale pose (Tolasana) lifting legs",
        "lighting": "soft light",
    },
    {
        "api": "replicate",
        "model": "black-forest-labs/flux-dev",
        "name": "bird_paradise_golden",
        "pose": "Bird of Paradise pose standing balance",
        "lighting": "golden hour",
    },
    # Hugging Face Spaces - FLUX.1 (15 poses)
    {
        "api": "huggingface",
        "model": "black-forest-labs/FLUX.1-schnell",
        "name": "camel_pose_sunrise",
        "pose": "Camel pose (Ustrasana) kneeling backbend",
        "lighting": "sunrise",
    },
    {
        "api": "huggingface",
        "model": "black-forest-labs/FLUX.1-schnell",
        "name": "wheel_pose_sunset",
        "pose": "Wheel pose (Urdhva Dhanurasana) full backbend",
        "lighting": "sunset",
    },
    {
        "api": "huggingface",
        "model": "black-forest-labs/FLUX.1-schnell",
        "name": "cobra_pose_morning",
        "pose": "Cobra pose (Bhujangasana) chest opening",
        "lighting": "morning",
    },
    {
        "api": "huggingface",
        "model": "black-forest-labs/FLUX.1-schnell",
        "name": "bridge_pose_midday",
        "pose": "Bridge pose (Setu Bandhasana) hip opening",
        "lighting": "bright sun",
    },
    {
        "api": "huggingface",
        "model": "black-forest-labs/FLUX.1-schnell",
        "name": "fish_pose_sunset",
        "pose": "Fish pose (Matsyasana) heart opening",
        "lighting": "sunset",
    },
    {
        "api": "huggingface",
        "model": "black-forest-labs/FLUX.1-schnell",
        "name": "bow_pose_morning",
        "pose": "Bow pose (Dhanurasana) full body stretch",
        "lighting": "morning light",
    },
    {
        "api": "huggingface",
        "model": "black-forest-labs/FLUX.1-schnell",
        "name": "scorpion_pose_advanced",
        "pose": "Scorpion pose (Vrschikasana) forearm stand backbend",
        "lighting": "golden hour",
    },
    {
        "api": "huggingface",
        "model": "black-forest-labs/FLUX.1-schnell",
        "name": "king_pigeon_sunset",
        "pose": "King Pigeon pose (Rajakapotasana) deep backbend",
        "lighting": "sunset",
    },
    {
        "api": "huggingface",
        "model": "black-forest-labs/FLUX.1-schnell",
        "name": "headstand_sunrise",
        "pose": "Headstand (Sirsasana) supported inversion",
        "lighting": "sunrise",
    },
    {
        "api": "huggingface",
        "model": "black-forest-labs/FLUX.1-schnell",
        "name": "shoulderstand_morning",
        "pose": "Shoulderstand (Sarvangasana) classic inversion",
        "lighting": "morning",
    },
    {
        "api": "huggingface",
        "model": "black-forest-labs/FLUX.1-schnell",
        "name": "forearm_stand_sunset",
        "pose": "Forearm Stand (Pincha Mayurasana) against wall",
        "lighting": "sunset",
    },
    {
        "api": "huggingface",
        "model": "black-forest-labs/FLUX.1-schnell",
        "name": "handstand_midday",
        "pose": "Handstand (Adho Mukha Vrksasana) full inversion",
        "lighting": "bright sun",
    },
    {
        "api": "huggingface",
        "model": "black-forest-labs/FLUX.1-schnell",
        "name": "supported_headstand",
        "pose": "Supported Headstand with forearms",
        "lighting": "soft light",
    },
    {
        "api": "huggingface",
        "model": "black-forest-labs/FLUX.1-schnell",
        "name": "legs_up_wall_sunset",
        "pose": "Legs-Up-the-Wall pose (Viparita Karani) restorative",
        "lighting": "sunset",
    },
    {
        "api": "huggingface",
        "model": "black-forest-labs/FLUX.1-schnell",
        "name": "plow_pose_morning",
        "pose": "Plow pose (Halasana) shoulder stand variation",
        "lighting": "morning light",
    },
]


async def generate_with_fal(pose_info, index):
    """Generate image using fal.ai API"""
    try:
        print(f"   🟦 fal.ai: Generating {pose_info['name']}...")

        prompt = BASE_PROMPTS["fal"].format(
            pose=pose_info["pose"], lighting=pose_info["lighting"]
        )

        result = fal_client.subscribe(
            pose_info["model"],
            arguments={
                "prompt": prompt,
                "negative_prompt": NEGATIVE_PROMPT,
                "image_size": "landscape_4_3",
                "num_inference_steps": 4,  # Fast generation
                "seed": random.randint(1, 2**32 - 1),
                "enable_safety_checker": True,
            },
        )

        if result and "images" in result and len(result["images"]) > 0:
            image_url = result["images"][0]["url"]

            # Download image
            async with aiohttp.ClientSession() as session:
                async with session.get(image_url) as response:
                    if response.status == 200:
                        filename = f"yoga_{pose_info['name']}_{index:03d}_fal.jpg"
                        with open(f"generated_images/{filename}", "wb") as f:
                            f.write(await response.read())

                        print(f"   ✅ fal.ai: {pose_info['name']} completed!")
                        return {
                            "index": index,
                            "name": pose_info["name"],
                            "api": "fal.ai",
                            "model": pose_info["model"],
                            "status": "success",
                            "filename": filename,
                            "prompt": prompt,
                            "timestamp": datetime.now().isoformat(),
                        }

        return {
            "index": index,
            "name": pose_info["name"],
            "api": "fal.ai",
            "status": "failed",
            "error": "No image in response",
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        print(f"   ❌ fal.ai: {pose_info['name']} failed - {e}")
        return {
            "index": index,
            "name": pose_info["name"],
            "api": "fal.ai",
            "status": "failed",
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
        }


def generate_with_replicate(pose_info, index):
    """Generate image using Replicate API"""
    try:
        print(f"   🟪 Replicate: Generating {pose_info['name']}...")

        prompt = BASE_PROMPTS["replicate"].format(
            pose=pose_info["pose"], lighting=pose_info["lighting"]
        )

        output = replicate_client.run(
            pose_info["model"],
            input={
                "prompt": prompt,
                "negative_prompt": NEGATIVE_PROMPT,
                "width": 1024,
                "height": 768,
                "num_inference_steps": 25,
                "guidance_scale": 3.5,
                "seed": random.randint(1, 2**32 - 1),
            },
        )

        if output and len(output) > 0:
            image_url = output[0]

            # Download image
            import urllib.request

            filename = f"yoga_{pose_info['name']}_{index:03d}_replicate.jpg"
            urllib.request.urlretrieve(image_url, f"generated_images/{filename}")

            print(f"   ✅ Replicate: {pose_info['name']} completed!")
            return {
                "index": index,
                "name": pose_info["name"],
                "api": "replicate",
                "model": pose_info["model"],
                "status": "success",
                "filename": filename,
                "prompt": prompt,
                "timestamp": datetime.now().isoformat(),
            }

        return {
            "index": index,
            "name": pose_info["name"],
            "api": "replicate",
            "status": "failed",
            "error": "No output received",
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        print(f"   ❌ Replicate: {pose_info['name']} failed - {e}")
        return {
            "index": index,
            "name": pose_info["name"],
            "api": "replicate",
            "status": "failed",
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
        }


def generate_with_huggingface(pose_info, index):
    """Generate image using Hugging Face Spaces"""
    try:
        print(f"   🟨 HuggingFace: Generating {pose_info['name']}...")

        prompt = BASE_PROMPTS["huggingface"].format(
            pose=pose_info["pose"], lighting=pose_info["lighting"]
        )

        # Try multiple HF spaces that host FLUX
        spaces = [
            "multimodalart/FLUX.1-merged",
            "black-forest-labs/FLUX.1-schnell",
            "gokaygokay/FLUX.1-merged",
        ]

        for space in spaces:
            try:
                client = Client(space, hf_token=HF_TOKEN)
                result = client.predict(
                    prompt=prompt,
                    seed=random.randint(1, 2**32 - 1),
                    width=1024,
                    height=768,
                    guidance_scale=3.5,
                    num_inference_steps=25,
                    api_name="/infer",
                )

                if result and isinstance(result, (str, Path)):
                    # Copy result to our directory
                    filename = f"yoga_{pose_info['name']}_{index:03d}_hf.jpg"
                    import shutil

                    shutil.copy(str(result), f"generated_images/{filename}")

                    print(f"   ✅ HuggingFace: {pose_info['name']} completed!")
                    return {
                        "index": index,
                        "name": pose_info["name"],
                        "api": "huggingface",
                        "space": space,
                        "status": "success",
                        "filename": filename,
                        "prompt": prompt,
                        "timestamp": datetime.now().isoformat(),
                    }

            except Exception as space_error:
                print(f"   ⚠️  Space {space} failed: {space_error}")
                continue

        return {
            "index": index,
            "name": pose_info["name"],
            "api": "huggingface",
            "status": "failed",
            "error": "All HF spaces failed",
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        print(f"   ❌ HuggingFace: {pose_info['name']} failed - {e}")
        return {
            "index": index,
            "name": pose_info["name"],
            "api": "huggingface",
            "status": "failed",
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
        }


async def generate_all_images():
    """Generate all 50 images using multiple APIs concurrently"""
    print("🧘‍♀️ Starting Multi-API Yoga Beach Image Generation!")
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # Create output directory
    Path("generated_images").mkdir(exist_ok=True)

    # Statistics
    api_counts = {"fal": 0, "replicate": 0, "huggingface": 0}
    for pose in YOGA_POSES:
        api_counts[pose["api"]] += 1

    print(f"📊 Distribution:")
    print(f"   🟦 fal.ai (FLUX Schnell): {api_counts['fal']} images")
    print(f"   🟪 Replicate (FLUX-dev): {api_counts['replicate']} images")
    print(f"   🟨 HuggingFace Spaces: {api_counts['huggingface']} images")
    print(f"   🎯 Total: {len(YOGA_POSES)} images")
    print()

    start_time = time.time()
    results = []

    # Create concurrent tasks
    tasks = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        for i, pose_info in enumerate(YOGA_POSES, 1):
            if pose_info["api"] == "fal":
                task = asyncio.create_task(generate_with_fal(pose_info, i))
                tasks.append(task)
            elif pose_info["api"] == "replicate":
                future = executor.submit(generate_with_replicate, pose_info, i)
                tasks.append(future)
            elif pose_info["api"] == "huggingface":
                future = executor.submit(generate_with_huggingface, pose_info, i)
                tasks.append(future)

        # Process completed tasks
        completed = 0
        failed = 0

        # Handle async tasks (fal.ai)
        async_tasks = [t for t in tasks if hasattr(t, "add_done_callback")]
        if async_tasks:
            async_results = await asyncio.gather(*async_tasks, return_exceptions=True)
            for result in async_results:
                if isinstance(result, Exception):
                    failed += 1
                else:
                    results.append(result)
                    if result.get("status") == "success":
                        completed += 1
                    else:
                        failed += 1

        # Handle sync tasks (replicate, huggingface)
        sync_tasks = [t for t in tasks if not hasattr(t, "add_done_callback")]
        for future in as_completed(sync_tasks):
            result = future.result()
            results.append(result)
            if result.get("status") == "success":
                completed += 1
            else:
                failed += 1

            # Progress update
            total_done = completed + failed
            if total_done % 10 == 0 or total_done == len(YOGA_POSES):
                elapsed = time.time() - start_time
                print(
                    f"\n📊 Progress: {total_done}/{len(YOGA_POSES)} ({completed} ✅, {failed} ❌)"
                )
                print(
                    f"⏱️  Elapsed: {elapsed/60:.1f} min, Avg: {elapsed/total_done:.1f}s per image"
                )

    # Final statistics
    total_time = time.time() - start_time

    # Save detailed log
    log_data = {
        "timestamp": datetime.now().isoformat(),
        "total_requested": len(YOGA_POSES),
        "successful": completed,
        "failed": failed,
        "total_time_minutes": total_time / 60,
        "api_distribution": api_counts,
        "results": results,
    }

    with open("multi_api_generation_log.json", "w") as f:
        json.dump(log_data, f, indent=2)

    print("\n" + "=" * 60)
    print(f"🎉 Multi-API Generation Complete!")
    print(f"✅ Successfully generated: {completed}/{len(YOGA_POSES)} images")
    print(f"❌ Failed: {failed}/{len(YOGA_POSES)} images")
    print(f"⏱️  Total time: {total_time/60:.1f} minutes")
    print(f"⚡ Average speed: {total_time/completed:.1f}s per successful image")
    print(f"📁 Images saved in: ./generated_images/")
    print(f"📝 Detailed log: multi_api_generation_log.json")

    # API success breakdown
    api_success = {"fal": 0, "replicate": 0, "huggingface": 0}
    for result in results:
        if result.get("status") == "success":
            api_success[result.get("api", "unknown")] += 1

    print(f"\n📊 Success by API:")
    print(f"   🟦 fal.ai: {api_success.get('fal', 0)}/{api_counts['fal']}")
    print(
        f"   🟪 Replicate: {api_success.get('replicate', 0)}/{api_counts['replicate']}"
    )
    print(
        f"   🟨 HuggingFace: {api_success.get('huggingface', 0)}/{api_counts['huggingface']}"
    )

    return completed, failed


if __name__ == "__main__":
    print("🚀 Multi-API Cloud Yoga Beach Image Generator")
    print("Using fal.ai + Replicate + HuggingFace for distributed generation")
    print("=" * 60)

    # Run the generation
    asyncio.run(generate_all_images())
