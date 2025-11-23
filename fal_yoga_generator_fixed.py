#!/usr/bin/env python3
"""
fal.ai Cloud Yoga Beach Image Generator
High-speed generation using fal.ai's FLUX models
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

# Import and configure fal client
try:
    import fal

    # Set the API key as environment variable
    os.environ["FAL_KEY"] = FAL_API
    print("✅ fal.ai client configured successfully")
except ImportError as e:
    print(f"❌ Missing fal-client: {e}")
    sys.exit(1)

# Enhanced prompts optimized for FLUX
BASE_PROMPT = """professional lifestyle photography, beautiful physically fit woman in mid-20s practicing {pose} on pristine summer beach during {lighting}, perfect anatomy, athletic toned physique, yoga athletic wear, serene peaceful expression, clear ocean waves background, white sandy beach, natural lighting, detailed skin textures, high contrast, vibrant warm colors, award winning photography, masterpiece, 8k uhd, sharp focus"""

NEGATIVE_PROMPT = "deformed anatomy, distorted limbs, poorly drawn hands, bad anatomy, extra limbs, missing limbs, mutation, ugly, blurry, low quality, cartoon, anime, 3d render, plastic skin"

# 50 Diverse Yoga poses for fal.ai generation
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
    {
        "name": "chair_pose_midday",
        "pose": "Chair pose (Utkatasana) with arms raised",
        "lighting": "bright sun",
    },
    {
        "name": "revolved_triangle_golden",
        "pose": "Revolved Triangle pose with spinal twist",
        "lighting": "golden hour",
    },
    {
        "name": "high_lunge_sunrise",
        "pose": "High Lunge pose with arms overhead",
        "lighting": "sunrise",
    },
    {
        "name": "crescent_lunge_natural",
        "pose": "Crescent Lunge pose",
        "lighting": "natural daylight",
    },
    {
        "name": "star_pose_sunset",
        "pose": "Star pose (Utthita Tadasana) with arms and legs wide",
        "lighting": "sunset glow",
    },
    {
        "name": "lotus_pose_morning",
        "pose": "Lotus pose (Padmasana) meditation position",
        "lighting": "soft morning",
    },
    {
        "name": "seated_forward_fold",
        "pose": "Seated Forward Fold (Paschimottanasana)",
        "lighting": "natural light",
    },
    {
        "name": "bound_angle_pose",
        "pose": "Bound Angle pose (Baddha Konasana) butterfly position",
        "lighting": "golden hour",
    },
    {
        "name": "seated_twist_right",
        "pose": "Seated Spinal Twist (Ardha Matsyendrasana)",
        "lighting": "sunset",
    },
    {
        "name": "hero_pose_sunset",
        "pose": "Hero pose (Virasana) kneeling meditation",
        "lighting": "sunset",
    },
    {
        "name": "sage_pose_morning",
        "pose": "Sage pose (Marichyasana) with arm bind",
        "lighting": "morning",
    },
    {
        "name": "easy_pose_midday",
        "pose": "Easy pose (Sukhasana) cross-legged",
        "lighting": "bright daylight",
    },
    {
        "name": "compass_pose_advanced",
        "pose": "Compass pose (Parivrtta Surya Yantrasana)",
        "lighting": "natural",
    },
    {
        "name": "seated_wide_leg_fold",
        "pose": "Seated Wide-Legged Forward Fold",
        "lighting": "soft light",
    },
    {
        "name": "boat_pose_sunset",
        "pose": "Boat pose (Navasana) core strengthening",
        "lighting": "sunset",
    },
    {
        "name": "crow_pose_morning",
        "pose": "Crow pose (Bakasana) arm balance",
        "lighting": "morning light",
    },
    {
        "name": "side_crow_sunset",
        "pose": "Side Crow pose advanced arm balance",
        "lighting": "sunset",
    },
    {
        "name": "dancers_pose_sunrise",
        "pose": "Dancer's pose (Natarajasana) standing backbend",
        "lighting": "sunrise",
    },
    {
        "name": "standing_hand_to_toe",
        "pose": "Standing Hand-to-Big-Toe pose",
        "lighting": "natural",
    },
    {
        "name": "eight_angle_pose",
        "pose": "Eight-Angle pose (Astavakrasana) advanced twist",
        "lighting": "golden hour",
    },
    {
        "name": "firefly_pose_challenging",
        "pose": "Firefly pose (Tittibhasana) arm balance",
        "lighting": "midday",
    },
    {
        "name": "side_plank_sunset",
        "pose": "Side Plank pose (Vasisthasana)",
        "lighting": "sunset",
    },
    {
        "name": "flying_pigeon_advanced",
        "pose": "Flying Pigeon pose arm balance",
        "lighting": "morning",
    },
    {
        "name": "scale_pose_strength",
        "pose": "Scale pose (Tolasana) lifting legs",
        "lighting": "soft light",
    },
    {
        "name": "bird_paradise_golden",
        "pose": "Bird of Paradise pose standing balance",
        "lighting": "golden hour",
    },
    {
        "name": "camel_pose_sunrise",
        "pose": "Camel pose (Ustrasana) kneeling backbend",
        "lighting": "sunrise",
    },
    {
        "name": "wheel_pose_sunset",
        "pose": "Wheel pose (Urdhva Dhanurasana) full backbend",
        "lighting": "sunset",
    },
    {
        "name": "cobra_pose_morning",
        "pose": "Cobra pose (Bhujangasana) chest opening",
        "lighting": "morning",
    },
    {
        "name": "bridge_pose_midday",
        "pose": "Bridge pose (Setu Bandhasana) hip opening",
        "lighting": "bright sun",
    },
    {
        "name": "fish_pose_sunset",
        "pose": "Fish pose (Matsyasana) heart opening",
        "lighting": "sunset",
    },
    {
        "name": "bow_pose_morning",
        "pose": "Bow pose (Dhanurasana) full body stretch",
        "lighting": "morning light",
    },
    {
        "name": "scorpion_pose_advanced",
        "pose": "Scorpion pose (Vrschikasana) forearm stand backbend",
        "lighting": "golden hour",
    },
    {
        "name": "king_pigeon_sunset",
        "pose": "King Pigeon pose (Rajakapotasana) deep backbend",
        "lighting": "sunset",
    },
    {
        "name": "headstand_sunrise",
        "pose": "Headstand (Sirsasana) supported inversion",
        "lighting": "sunrise",
    },
    {
        "name": "shoulderstand_morning",
        "pose": "Shoulderstand (Sarvangasana) classic inversion",
        "lighting": "morning",
    },
    {
        "name": "forearm_stand_sunset",
        "pose": "Forearm Stand (Pincha Mayurasana) against wall",
        "lighting": "sunset",
    },
    {
        "name": "handstand_midday",
        "pose": "Handstand (Adho Mukha Vrksasana) full inversion",
        "lighting": "bright sun",
    },
    {
        "name": "supported_headstand",
        "pose": "Supported Headstand with forearms",
        "lighting": "soft light",
    },
    {
        "name": "legs_up_wall_sunset",
        "pose": "Legs-Up-the-Wall pose (Viparita Karani) restorative",
        "lighting": "sunset",
    },
    {
        "name": "plow_pose_morning",
        "pose": "Plow pose (Halasana) shoulder stand variation",
        "lighting": "morning light",
    },
]


async def generate_single_image(pose_info, index, semaphore):
    """Generate a single image using fal.ai with rate limiting"""
    async with semaphore:  # Limit concurrent requests
        try:
            print(f"📸 {index:2d}/50: Generating {pose_info['name']}")

            prompt = BASE_PROMPT.format(
                pose=pose_info["pose"], lighting=pose_info["lighting"]
            )

            # Use fal.ai FLUX.1 [schnell] for speed
            result = fal.run(
                "fal-ai/flux/schnell",
                arguments={
                    "prompt": prompt,
                    "negative_prompt": NEGATIVE_PROMPT,
                    "image_size": "landscape_4_3",  # 1024x768
                    "num_inference_steps": 4,
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
                            filename = f"yoga_{pose_info['name']}_{index:03d}.jpg"
                            filepath = f"generated_images/{filename}"

                            with open(filepath, "wb") as f:
                                f.write(await response.read())

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
    """Generate all 50 images using fal.ai concurrently with rate limiting"""
    print("🧘‍♀️ fal.ai Yoga Beach Image Generation Started!")
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🟦 Using fal.ai FLUX.1 [schnell] for high-speed generation")
    print("=" * 60)

    # Create output directory
    Path("generated_images").mkdir(exist_ok=True)

    start_time = time.time()

    # Rate limiting: max 3 concurrent requests to be nice to fal.ai
    semaphore = asyncio.Semaphore(3)

    # Create all tasks
    tasks = []
    for i, pose_info in enumerate(YOGA_POSES, 1):
        task = generate_single_image(pose_info, i, semaphore)
        tasks.append(task)

    # Run all tasks concurrently
    print(f"🚀 Launching {len(tasks)} concurrent generation tasks...")
    print()

    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Filter out exceptions and analyze results
    valid_results = [r for r in results if not isinstance(r, Exception)]
    exceptions = [r for r in results if isinstance(r, Exception)]

    successful = [r for r in valid_results if r.get("status") == "success"]
    failed = [r for r in valid_results if r.get("status") == "failed"]

    total_time = time.time() - start_time

    # Save detailed log
    log_data = {
        "generator": "fal.ai FLUX.1 schnell",
        "timestamp": datetime.now().isoformat(),
        "total_requested": len(YOGA_POSES),
        "successful": len(successful),
        "failed": len(failed) + len(exceptions),
        "success_rate": len(successful) / len(YOGA_POSES) * 100,
        "total_time_minutes": total_time / 60,
        "average_time_per_image": total_time / len(YOGA_POSES),
        "images": valid_results,
        "exceptions": [str(e) for e in exceptions],
    }

    with open("fal_yoga_generation_log.json", "w") as f:
        json.dump(log_data, f, indent=2)

    # Results summary
    print("\n" + "=" * 60)
    print(f"🎉 fal.ai Generation Complete!")
    print(
        f"✅ Successfully generated: {len(successful)}/{len(YOGA_POSES)} images ({len(successful)/len(YOGA_POSES)*100:.1f}%)"
    )
    print(f"❌ Failed: {len(failed) + len(exceptions)}/{len(YOGA_POSES)} images")
    if exceptions:
        print(f"⚠️  Exceptions: {len(exceptions)}")
    print(f"⏱️  Total time: {total_time/60:.1f} minutes")
    if successful:
        print(
            f"⚡ Average speed: {total_time/len(successful):.1f}s per successful image"
        )
    print(f"📁 Images saved in: ./generated_images/")
    print(f"📝 Detailed log: fal_yoga_generation_log.json")

    if successful:
        print(f"\n🖼️  Sample generated images:")
        for result in successful[:5]:  # Show first 5
            print(f"   - {result['filename']}: {result['pose']}")
        if len(successful) > 5:
            print(f"   ... and {len(successful)-5} more!")

    return len(successful), len(failed) + len(exceptions)


if __name__ == "__main__":
    print("🚀 fal.ai High-Speed Yoga Beach Generator")
    print("Generating 50 professional yoga images in minutes!")
    print("=" * 60)

    # Run the generation
    success_count, fail_count = asyncio.run(generate_all_images())

    print(f"\n🏁 Final Results:")
    if success_count >= 45:
        print("🎉 Excellent! Almost all images generated successfully!")
    elif success_count >= 35:
        print("👍 Great job! Most images generated successfully!")
    elif success_count >= 20:
        print("😊 Good results! Solid batch of images generated!")
    else:
        print("⚠️  Some issues encountered. Check the logs for details.")

    print(
        f"📊 Success Rate: {success_count}/{success_count+fail_count} ({success_count/(success_count+fail_count)*100:.1f}%)"
    )
