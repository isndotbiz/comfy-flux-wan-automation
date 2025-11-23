#!/usr/bin/env python3
"""
Complete 50-Image Hugging Face FLUX Yoga Beach Generator
Generates all 50 professional yoga beach images using HF Inference API
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
from config import HF_TOKEN, verify_secrets

# Verify secrets are loaded
if not verify_secrets():
    print("❌ HF_TOKEN not found!")
    sys.exit(1)

print(f"✅ Hugging Face token ready: {HF_TOKEN[:10]}...")

# Enhanced prompts optimized for FLUX
BASE_PROMPT = """professional lifestyle photography, beautiful physically fit woman in mid-20s practicing {pose} on pristine summer beach during {lighting}, perfect anatomy, athletic toned physique, yoga athletic wear, serene peaceful expression, clear ocean waves background, white sandy beach, natural lighting, detailed skin textures, high contrast, vibrant warm colors, award winning photography, masterpiece, 8k uhd, sharp focus"""

# Complete 50 yoga poses with diverse categories
YOGA_POSES = [
    # Standing Poses (15 poses)
    {
        "name": "warrior_I_sunrise",
        "pose": "Warrior I pose (Virabhadrasana I) with arms raised overhead",
        "lighting": "golden sunrise",
        "category": "standing",
    },
    {
        "name": "warrior_II_sunset",
        "pose": "Warrior II pose (Virabhadrasana II) with arms extended",
        "lighting": "warm sunset glow",
        "category": "standing",
    },
    {
        "name": "warrior_III_midday",
        "pose": "Warrior III pose (Virabhadrasana III) balancing on one leg",
        "lighting": "bright midday sun",
        "category": "standing",
    },
    {
        "name": "tree_pose_morning",
        "pose": "Tree pose (Vrksasana) with hands in prayer position",
        "lighting": "soft morning light",
        "category": "standing",
    },
    {
        "name": "triangle_pose_sunset",
        "pose": "Triangle pose (Trikonasana) with hand on ankle",
        "lighting": "golden sunset",
        "category": "standing",
    },
    {
        "name": "extended_triangle_golden",
        "pose": "Extended Triangle pose (Utthita Trikonasana)",
        "lighting": "golden hour",
        "category": "standing",
    },
    {
        "name": "mountain_pose_sunrise",
        "pose": "Mountain pose (Tadasana) standing tall",
        "lighting": "sunrise glow",
        "category": "standing",
    },
    {
        "name": "standing_forward_fold",
        "pose": "Standing Forward Fold (Uttanasana)",
        "lighting": "soft diffused light",
        "category": "standing",
    },
    {
        "name": "eagle_pose_morning",
        "pose": "Eagle pose (Garudasana) with arms and legs wrapped",
        "lighting": "morning light",
        "category": "standing",
    },
    {
        "name": "goddess_pose_sunset",
        "pose": "Goddess pose (Utkata Konasana) wide-legged squat",
        "lighting": "sunset",
        "category": "standing",
    },
    {
        "name": "chair_pose_midday",
        "pose": "Chair pose (Utkatasana) with arms raised",
        "lighting": "bright sun",
        "category": "standing",
    },
    {
        "name": "revolved_triangle_golden",
        "pose": "Revolved Triangle pose with spinal twist",
        "lighting": "golden hour",
        "category": "standing",
    },
    {
        "name": "high_lunge_sunrise",
        "pose": "High Lunge pose with arms overhead",
        "lighting": "sunrise",
        "category": "standing",
    },
    {
        "name": "crescent_lunge_natural",
        "pose": "Crescent Lunge pose",
        "lighting": "natural daylight",
        "category": "standing",
    },
    {
        "name": "star_pose_sunset",
        "pose": "Star pose (Utthita Tadasana) with arms and legs wide",
        "lighting": "sunset glow",
        "category": "standing",
    },
    # Seated Poses (10 poses)
    {
        "name": "lotus_pose_morning",
        "pose": "Lotus pose (Padmasana) meditation position",
        "lighting": "soft morning",
        "category": "seated",
    },
    {
        "name": "seated_forward_fold",
        "pose": "Seated Forward Fold (Paschimottanasana)",
        "lighting": "natural light",
        "category": "seated",
    },
    {
        "name": "bound_angle_pose",
        "pose": "Bound Angle pose (Baddha Konasana) butterfly position",
        "lighting": "golden hour",
        "category": "seated",
    },
    {
        "name": "seated_twist_right",
        "pose": "Seated Spinal Twist (Ardha Matsyendrasana)",
        "lighting": "sunset",
        "category": "seated",
    },
    {
        "name": "hero_pose_sunset",
        "pose": "Hero pose (Virasana) kneeling meditation",
        "lighting": "sunset",
        "category": "seated",
    },
    {
        "name": "sage_pose_morning",
        "pose": "Sage pose (Marichyasana) with arm bind",
        "lighting": "morning",
        "category": "seated",
    },
    {
        "name": "easy_pose_midday",
        "pose": "Easy pose (Sukhasana) cross-legged",
        "lighting": "bright daylight",
        "category": "seated",
    },
    {
        "name": "compass_pose_advanced",
        "pose": "Compass pose (Parivrtta Surya Yantrasana)",
        "lighting": "natural",
        "category": "seated",
    },
    {
        "name": "seated_wide_leg_fold",
        "pose": "Seated Wide-Legged Forward Fold",
        "lighting": "soft light",
        "category": "seated",
    },
    {
        "name": "boat_pose_sunset",
        "pose": "Boat pose (Navasana) core strengthening",
        "lighting": "sunset",
        "category": "seated",
    },
    # Balance Poses (10 poses)
    {
        "name": "crow_pose_morning",
        "pose": "Crow pose (Bakasana) arm balance",
        "lighting": "morning light",
        "category": "balance",
    },
    {
        "name": "side_crow_sunset",
        "pose": "Side Crow pose advanced arm balance",
        "lighting": "sunset",
        "category": "balance",
    },
    {
        "name": "dancers_pose_sunrise",
        "pose": "Dancer's pose (Natarajasana) standing backbend",
        "lighting": "sunrise",
        "category": "balance",
    },
    {
        "name": "standing_hand_to_toe",
        "pose": "Standing Hand-to-Big-Toe pose",
        "lighting": "natural",
        "category": "balance",
    },
    {
        "name": "eight_angle_pose",
        "pose": "Eight-Angle pose (Astavakrasana) advanced twist",
        "lighting": "golden hour",
        "category": "balance",
    },
    {
        "name": "firefly_pose_challenging",
        "pose": "Firefly pose (Tittibhasana) arm balance",
        "lighting": "midday",
        "category": "balance",
    },
    {
        "name": "side_plank_sunset",
        "pose": "Side Plank pose (Vasisthasana)",
        "lighting": "sunset",
        "category": "balance",
    },
    {
        "name": "flying_pigeon_advanced",
        "pose": "Flying Pigeon pose arm balance",
        "lighting": "morning",
        "category": "balance",
    },
    {
        "name": "scale_pose_strength",
        "pose": "Scale pose (Tolasana) lifting legs",
        "lighting": "soft light",
        "category": "balance",
    },
    {
        "name": "bird_paradise_golden",
        "pose": "Bird of Paradise pose standing balance",
        "lighting": "golden hour",
        "category": "balance",
    },
    # Backbends (8 poses)
    {
        "name": "camel_pose_sunrise",
        "pose": "Camel pose (Ustrasana) kneeling backbend",
        "lighting": "sunrise",
        "category": "backbend",
    },
    {
        "name": "wheel_pose_sunset",
        "pose": "Wheel pose (Urdhva Dhanurasana) full backbend",
        "lighting": "sunset",
        "category": "backbend",
    },
    {
        "name": "cobra_pose_morning",
        "pose": "Cobra pose (Bhujangasana) chest opening",
        "lighting": "morning",
        "category": "backbend",
    },
    {
        "name": "bridge_pose_midday",
        "pose": "Bridge pose (Setu Bandhasana) hip opening",
        "lighting": "bright sun",
        "category": "backbend",
    },
    {
        "name": "fish_pose_sunset",
        "pose": "Fish pose (Matsyasana) heart opening",
        "lighting": "sunset",
        "category": "backbend",
    },
    {
        "name": "bow_pose_morning",
        "pose": "Bow pose (Dhanurasana) full body stretch",
        "lighting": "morning light",
        "category": "backbend",
    },
    {
        "name": "scorpion_pose_advanced",
        "pose": "Scorpion pose (Vrschikasana) forearm stand backbend",
        "lighting": "golden hour",
        "category": "backbend",
    },
    {
        "name": "king_pigeon_sunset",
        "pose": "King Pigeon pose (Rajakapotasana) deep backbend",
        "lighting": "sunset",
        "category": "backbend",
    },
    # Inversions (7 poses)
    {
        "name": "headstand_sunrise",
        "pose": "Headstand (Sirsasana) supported inversion",
        "lighting": "sunrise",
        "category": "inversion",
    },
    {
        "name": "shoulderstand_morning",
        "pose": "Shoulderstand (Sarvangasana) classic inversion",
        "lighting": "morning",
        "category": "inversion",
    },
    {
        "name": "forearm_stand_sunset",
        "pose": "Forearm Stand (Pincha Mayurasana) against wall",
        "lighting": "sunset",
        "category": "inversion",
    },
    {
        "name": "handstand_midday",
        "pose": "Handstand (Adho Mukha Vrksasana) full inversion",
        "lighting": "bright sun",
        "category": "inversion",
    },
    {
        "name": "supported_headstand",
        "pose": "Supported Headstand with forearms",
        "lighting": "soft light",
        "category": "inversion",
    },
    {
        "name": "legs_up_wall_sunset",
        "pose": "Legs-Up-the-Wall pose (Viparita Karani) restorative",
        "lighting": "sunset",
        "category": "inversion",
    },
    {
        "name": "plow_pose_morning",
        "pose": "Plow pose (Halasana) shoulder stand variation",
        "lighting": "morning light",
        "category": "inversion",
    },
]


async def generate_single_image_hf(session, pose_info, index):
    """Generate a single image using Hugging Face Inference API"""
    try:
        print(
            f"📸 {index:2d}/50: {pose_info['category'].title()} - {pose_info['name']}"
        )

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

        # Make the API call with retries
        for attempt in range(3):  # Up to 3 attempts
            try:
                async with session.post(
                    url, json=payload, headers=headers, timeout=120
                ) as response:
                    if response.status == 200:
                        # HF returns image bytes directly
                        image_data = await response.read()

                        # Save the image
                        filename = f"yoga_{pose_info['name']}_{index:03d}.jpg"
                        filepath = f"generated_images/{filename}"

                        with open(filepath, "wb") as f:
                            f.write(image_data)

                        print(f"   ✅ Completed! -> {filename}")
                        return {
                            "index": index,
                            "name": pose_info["name"],
                            "pose": pose_info["pose"],
                            "category": pose_info["category"],
                            "status": "success",
                            "filename": filename,
                            "prompt": prompt[:100] + "...",  # Truncated for log
                            "lighting": pose_info["lighting"],
                            "timestamp": datetime.now().isoformat(),
                            "api": "huggingface",
                            "attempt": attempt + 1,
                        }

                    elif response.status == 503:
                        error_text = await response.text()
                        if "loading" in error_text.lower() and attempt < 2:
                            print(
                                f"   ⏳ Model loading, retrying in 15s... (attempt {attempt + 1})"
                            )
                            await asyncio.sleep(15)
                            continue
                        else:
                            print(f"   ❌ Service unavailable after retries")
                            return {
                                "index": index,
                                "name": pose_info["name"],
                                "status": "failed",
                                "error": f"Service unavailable: {error_text[:200]}",
                                "timestamp": datetime.now().isoformat(),
                            }
                    else:
                        error_text = await response.text()
                        if attempt < 2:
                            print(
                                f"   ⚠️  HTTP {response.status}, retrying... (attempt {attempt + 1})"
                            )
                            await asyncio.sleep(10)
                            continue
                        else:
                            print(
                                f"   ❌ Failed after retries - HTTP {response.status}"
                            )
                            return {
                                "index": index,
                                "name": pose_info["name"],
                                "status": "failed",
                                "error": f"HTTP {response.status}: {error_text[:200]}",
                                "timestamp": datetime.now().isoformat(),
                            }

            except Exception as e:
                if attempt < 2:
                    print(
                        f"   ⚠️  Exception: {str(e)[:50]}, retrying... (attempt {attempt + 1})"
                    )
                    await asyncio.sleep(10)
                    continue
                else:
                    print(f"   ❌ Failed after retries - {str(e)[:100]}")
                    return {
                        "index": index,
                        "name": pose_info["name"],
                        "status": "failed",
                        "error": str(e),
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


async def generate_all_50_images():
    """Generate all 50 yoga beach images"""
    print("🧘‍♀️ Complete 50-Image Yoga Beach Generation!")
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🤗 Using Hugging Face FLUX.1 Schnell API")
    print("=" * 70)

    # Category breakdown
    categories = {}
    for pose in YOGA_POSES:
        cat = pose["category"]
        categories[cat] = categories.get(cat, 0) + 1

    print("📊 Yoga Pose Distribution:")
    for cat, count in categories.items():
        print(f"   {cat.title()}: {count} poses")
    print(f"   🎯 Total: {len(YOGA_POSES)} images")
    print()

    # Create output directory
    Path("generated_images").mkdir(exist_ok=True)

    start_time = time.time()

    # Create session with generous timeouts
    timeout = aiohttp.ClientTimeout(total=300, connect=60)

    async with aiohttp.ClientSession(timeout=timeout) as session:
        results = []
        successful = 0
        failed = 0

        # Generate images sequentially with progress tracking
        for i, pose_info in enumerate(YOGA_POSES, 1):
            result = await generate_single_image_hf(session, pose_info, i)
            results.append(result)

            if result.get("status") == "success":
                successful += 1
            else:
                failed += 1

            # Progress update every 10 images
            if i % 10 == 0:
                elapsed = time.time() - start_time
                avg_time = elapsed / i
                remaining = (50 - i) * avg_time
                print(f"\n📊 Progress: {i}/50 ({successful} ✅, {failed} ❌)")
                print(
                    f"⏱️  Elapsed: {elapsed/60:.1f}min, Remaining: ~{remaining/60:.1f}min"
                )
                print(f"⚡ Average: {avg_time:.1f}s per image")
                print()

            # Rate limiting - be nice to Hugging Face
            if i < len(YOGA_POSES):
                await asyncio.sleep(3)  # 3 second delay between requests

    # Final analysis
    total_time = time.time() - start_time

    # Save comprehensive log
    log_data = {
        "generator": "Hugging Face FLUX.1 Schnell - Complete 50 Images",
        "timestamp": datetime.now().isoformat(),
        "total_requested": len(YOGA_POSES),
        "successful": successful,
        "failed": failed,
        "success_rate": successful / len(YOGA_POSES) * 100,
        "total_time_minutes": total_time / 60,
        "average_time_per_image": total_time / len(YOGA_POSES),
        "category_breakdown": categories,
        "images": results,
    }

    with open("complete_50_yoga_generation_log.json", "w") as f:
        json.dump(log_data, f, indent=2)

    # Results summary
    print("\n" + "=" * 70)
    print(f"🎉 COMPLETE 50-IMAGE GENERATION FINISHED!")
    print(
        f"✅ Successfully generated: {successful}/50 images ({successful/50*100:.1f}%)"
    )
    print(f"❌ Failed: {failed}/50 images")
    print(f"⏱️  Total time: {total_time/60:.1f} minutes ({total_time/60/60:.1f} hours)")
    if successful > 0:
        print(f"⚡ Average speed: {total_time/successful:.1f}s per successful image")
    print(f"📁 Images saved in: ./generated_images/")
    print(f"📝 Detailed log: complete_50_yoga_generation_log.json")

    # Category success breakdown
    cat_success = {}
    for result in results:
        if result.get("status") == "success":
            cat = result.get("category", "unknown")
            cat_success[cat] = cat_success.get(cat, 0) + 1

    print(f"\n📊 Success by Category:")
    for cat, total in categories.items():
        success_count = cat_success.get(cat, 0)
        print(
            f"   {cat.title()}: {success_count}/{total} ({success_count/total*100:.0f}%)"
        )

    if successful >= 45:
        print(f"\n🎉 OUTSTANDING RESULTS! Almost perfect generation!")
    elif successful >= 35:
        print(f"\n👏 EXCELLENT WORK! Great success rate!")
    elif successful >= 25:
        print(f"\n😊 GOOD JOB! Solid batch of images created!")

    print(f"\n🖼️  You now have {successful} professional yoga beach images!")
    print(f"📸 Ready for upload to Hugging Face, social media, or portfolio!")

    return successful, failed


if __name__ == "__main__":
    print("🚀 Ultimate 50-Image Yoga Beach Generator")
    print("Professional FLUX-generated yoga photography collection")
    print("=" * 70)

    # Confirm before starting
    print("⚠️  This will generate 50 high-quality images (~3-4 minutes)")
    print("💰 This will use Hugging Face API credits")

    # Run the complete generation
    success_count, fail_count = asyncio.run(generate_all_50_images())

    print(f"\n🏁 FINAL STATISTICS:")
    print(f"🎯 Target: 50 images")
    print(f"✅ Generated: {success_count}")
    print(f"❌ Failed: {fail_count}")
    print(f"📊 Success Rate: {success_count/(success_count+fail_count)*100:.1f}%")

    if success_count >= 40:
        print("\n🌟 MISSION ACCOMPLISHED! 🌟")
        print("You've created an amazing collection of yoga beach images!")
