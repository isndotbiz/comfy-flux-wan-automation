#!/usr/bin/env python3
"""
Enhanced Yoga Beach Image Generation Script for Remote GPU Server
Generates 50 high-quality yoga beach images using ComfyUI and Flux
Uses ~/Workspaces/secrets.env for credentials
"""

import sys
import os

sys.path.append("./src")

# Import centralized config
from config import COMFYUI_URL, HF_TOKEN, verify_secrets

import json
import requests
import random
import time
from datetime import datetime
from pathlib import Path

# Verify secrets are loaded
if not verify_secrets():
    sys.exit(1)

# Flux-optimized base prompt template with better anatomy focus
BASE_PROMPT = """professional lifestyle photography, beautiful physically fit woman in mid-20s practicing {pose} on pristine summer beach during {lighting}, perfect anatomy, athletic toned physique, yoga athletic wear, serene peaceful expression, clear ocean waves background, white sandy beach, natural lighting, detailed skin textures, high contrast, vibrant warm colors, award winning photography, masterpiece, 8k uhd, sharp focus"""

NEGATIVE_PROMPT = """deformed anatomy, distorted limbs, disfigured body, poorly drawn hands, bad anatomy, wrong anatomy, extra limbs, missing limbs, floating limbs, mutated hands and fingers, disconnected limbs, mutation, mutated body, ugly face, disgusting, blurry image, amputation, low quality, worst quality, cartoon style, anime, 3d render, artificial looking, plastic skin"""

# 50 Diverse Yoga poses with detailed descriptions, camera angles, and lighting
YOGA_POSES = [
    # Standing Poses (15 poses)
    {
        "name": "warrior_I_sunrise",
        "pose": "Warrior I pose (Virabhadrasana I) with arms raised overhead",
        "angle": "three-quarter front view",
        "lighting": "golden sunrise",
    },
    {
        "name": "warrior_II_sunset",
        "pose": "Warrior II pose (Virabhadrasana II) with arms extended",
        "angle": "side profile view",
        "lighting": "warm sunset glow",
    },
    {
        "name": "warrior_III_midday",
        "pose": "Warrior III pose (Virabhadrasana III) balancing on one leg",
        "angle": "side view",
        "lighting": "bright midday sun",
    },
    {
        "name": "tree_pose_morning",
        "pose": "Tree pose (Vrksasana) with hands in prayer position",
        "angle": "front view",
        "lighting": "soft morning light",
    },
    {
        "name": "triangle_pose_sunset",
        "pose": "Triangle pose (Trikonasana) with hand on ankle",
        "angle": "side profile",
        "lighting": "golden sunset",
    },
    {
        "name": "extended_triangle_golden",
        "pose": "Extended Triangle pose (Utthita Trikonasana)",
        "angle": "three-quarter view",
        "lighting": "golden hour",
    },
    {
        "name": "mountain_pose_sunrise",
        "pose": "Mountain pose (Tadasana) standing tall",
        "angle": "front view",
        "lighting": "sunrise glow",
    },
    {
        "name": "standing_forward_fold",
        "pose": "Standing Forward Fold (Uttanasana)",
        "angle": "side view",
        "lighting": "soft diffused light",
    },
    {
        "name": "eagle_pose_morning",
        "pose": "Eagle pose (Garudasana) with arms and legs wrapped",
        "angle": "front view",
        "lighting": "morning light",
    },
    {
        "name": "goddess_pose_sunset",
        "pose": "Goddess pose (Utkata Konasana) wide-legged squat",
        "angle": "front view",
        "lighting": "sunset",
    },
    {
        "name": "chair_pose_midday",
        "pose": "Chair pose (Utkatasana) with arms raised",
        "angle": "three-quarter view",
        "lighting": "bright sun",
    },
    {
        "name": "revolved_triangle_golden",
        "pose": "Revolved Triangle pose with spinal twist",
        "angle": "side profile",
        "lighting": "golden hour",
    },
    {
        "name": "high_lunge_sunrise",
        "pose": "High Lunge pose with arms overhead",
        "angle": "side view",
        "lighting": "sunrise",
    },
    {
        "name": "crescent_lunge_natural",
        "pose": "Crescent Lunge pose",
        "angle": "three-quarter view",
        "lighting": "natural daylight",
    },
    {
        "name": "star_pose_sunset",
        "pose": "Star pose (Utthita Tadasana) with arms and legs wide",
        "angle": "front view",
        "lighting": "sunset glow",
    },
    # Seated Poses (10 poses)
    {
        "name": "lotus_pose_morning",
        "pose": "Lotus pose (Padmasana) meditation position",
        "angle": "front view",
        "lighting": "soft morning",
    },
    {
        "name": "seated_forward_fold",
        "pose": "Seated Forward Fold (Paschimottanasana)",
        "angle": "side view",
        "lighting": "natural light",
    },
    {
        "name": "bound_angle_pose",
        "pose": "Bound Angle pose (Baddha Konasana) butterfly position",
        "angle": "front view",
        "lighting": "golden hour",
    },
    {
        "name": "seated_twist_right",
        "pose": "Seated Spinal Twist (Ardha Matsyendrasana)",
        "angle": "three-quarter view",
        "lighting": "sunset",
    },
    {
        "name": "hero_pose_sunset",
        "pose": "Hero pose (Virasana) kneeling meditation",
        "angle": "front view",
        "lighting": "sunset",
    },
    {
        "name": "sage_pose_morning",
        "pose": "Sage pose (Marichyasana) with arm bind",
        "angle": "side profile",
        "lighting": "morning",
    },
    {
        "name": "easy_pose_midday",
        "pose": "Easy pose (Sukhasana) cross-legged",
        "angle": "front view",
        "lighting": "bright daylight",
    },
    {
        "name": "compass_pose_advanced",
        "pose": "Compass pose (Parivrtta Surya Yantrasana)",
        "angle": "side view",
        "lighting": "natural",
    },
    {
        "name": "seated_wide_leg_fold",
        "pose": "Seated Wide-Legged Forward Fold",
        "angle": "front view",
        "lighting": "soft light",
    },
    {
        "name": "boat_pose_sunset",
        "pose": "Boat pose (Navasana) core strengthening",
        "angle": "three-quarter view",
        "lighting": "sunset",
    },
    # Balance Poses (10 poses)
    {
        "name": "crow_pose_morning",
        "pose": "Crow pose (Bakasana) arm balance",
        "angle": "side view",
        "lighting": "morning light",
    },
    {
        "name": "side_crow_sunset",
        "pose": "Side Crow pose advanced arm balance",
        "angle": "three-quarter view",
        "lighting": "sunset",
    },
    {
        "name": "dancers_pose_sunrise",
        "pose": "Dancer's pose (Natarajasana) standing backbend",
        "angle": "side profile",
        "lighting": "sunrise",
    },
    {
        "name": "standing_hand_to_toe",
        "pose": "Standing Hand-to-Big-Toe pose",
        "angle": "side view",
        "lighting": "natural",
    },
    {
        "name": "eight_angle_pose",
        "pose": "Eight-Angle pose (Astavakrasana) advanced twist",
        "angle": "side view",
        "lighting": "golden hour",
    },
    {
        "name": "firefly_pose_challenging",
        "pose": "Firefly pose (Tittibhasana) arm balance",
        "angle": "front view",
        "lighting": "midday",
    },
    {
        "name": "side_plank_sunset",
        "pose": "Side Plank pose (Vasisthasana)",
        "angle": "side profile",
        "lighting": "sunset",
    },
    {
        "name": "flying_pigeon_advanced",
        "pose": "Flying Pigeon pose arm balance",
        "angle": "three-quarter view",
        "lighting": "morning",
    },
    {
        "name": "scale_pose_strength",
        "pose": "Scale pose (Tolasana) lifting legs",
        "angle": "front view",
        "lighting": "soft light",
    },
    {
        "name": "bird_paradise_golden",
        "pose": "Bird of Paradise pose standing balance",
        "angle": "side view",
        "lighting": "golden hour",
    },
    # Backbends (8 poses)
    {
        "name": "camel_pose_sunrise",
        "pose": "Camel pose (Ustrasana) kneeling backbend",
        "angle": "three-quarter view",
        "lighting": "sunrise",
    },
    {
        "name": "wheel_pose_sunset",
        "pose": "Wheel pose (Urdhva Dhanurasana) full backbend",
        "angle": "side view",
        "lighting": "sunset",
    },
    {
        "name": "cobra_pose_morning",
        "pose": "Cobra pose (Bhujangasana) chest opening",
        "angle": "front view",
        "lighting": "morning",
    },
    {
        "name": "bridge_pose_midday",
        "pose": "Bridge pose (Setu Bandhasana) hip opening",
        "angle": "side profile",
        "lighting": "bright sun",
    },
    {
        "name": "fish_pose_sunset",
        "pose": "Fish pose (Matsyasana) heart opening",
        "angle": "three-quarter view",
        "lighting": "sunset",
    },
    {
        "name": "bow_pose_morning",
        "pose": "Bow pose (Dhanurasana) full body stretch",
        "angle": "side view",
        "lighting": "morning light",
    },
    {
        "name": "scorpion_pose_advanced",
        "pose": "Scorpion pose (Vrschikasana) forearm stand backbend",
        "angle": "side profile",
        "lighting": "golden hour",
    },
    {
        "name": "king_pigeon_sunset",
        "pose": "King Pigeon pose (Rajakapotasana) deep backbend",
        "angle": "three-quarter view",
        "lighting": "sunset",
    },
    # Inversions (7 poses)
    {
        "name": "headstand_sunrise",
        "pose": "Headstand (Sirsasana) supported inversion",
        "angle": "side view",
        "lighting": "sunrise",
    },
    {
        "name": "shoulderstand_morning",
        "pose": "Shoulderstand (Sarvangasana) classic inversion",
        "angle": "side profile",
        "lighting": "morning",
    },
    {
        "name": "forearm_stand_sunset",
        "pose": "Forearm Stand (Pincha Mayurasana) against wall",
        "angle": "side view",
        "lighting": "sunset",
    },
    {
        "name": "handstand_midday",
        "pose": "Handstand (Adho Mukha Vrksasana) full inversion",
        "angle": "side profile",
        "lighting": "bright sun",
    },
    {
        "name": "supported_headstand",
        "pose": "Supported Headstand with forearms",
        "angle": "three-quarter view",
        "lighting": "soft light",
    },
    {
        "name": "legs_up_wall_sunset",
        "pose": "Legs-Up-the-Wall pose (Viparita Karani) restorative",
        "angle": "side view",
        "lighting": "sunset",
    },
    {
        "name": "plow_pose_morning",
        "pose": "Plow pose (Halasana) shoulder stand variation",
        "angle": "side profile",
        "lighting": "morning light",
    },
]


def create_workflow(prompt, negative_prompt, seed=None):
    """Create ComfyUI workflow JSON optimized for Flux model"""
    if seed is None:
        seed = random.randint(1, 2**32 - 1)

    workflow = {
        "3": {
            "inputs": {
                "seed": seed,
                "steps": 28,  # Increased for better quality
                "cfg": 3.5,  # Optimized for Flux
                "sampler_name": "euler",
                "scheduler": "simple",
                "denoise": 1.0,
                "model": ["4", 0],
                "positive": ["6", 0],
                "negative": ["7", 0],
                "latent_image": ["5", 0],
            },
            "class_type": "KSampler",
        },
        "4": {
            "inputs": {"ckpt_name": "flux1-dev.sft"},  # Updated model name
            "class_type": "CheckpointLoaderSimple",
        },
        "5": {
            "inputs": {"width": 1024, "height": 1024, "batch_size": 1},
            "class_type": "EmptyLatentImage",
        },
        "6": {
            "inputs": {"text": prompt, "clip": ["4", 1]},
            "class_type": "CLIPTextEncode",
        },
        "7": {
            "inputs": {"text": negative_prompt, "clip": ["4", 1]},
            "class_type": "CLIPTextEncode",
        },
        "8": {
            "inputs": {"samples": ["3", 0], "vae": ["4", 2]},
            "class_type": "VAEDecode",
        },
        "9": {
            "inputs": {"filename_prefix": "yoga_beach_", "images": ["8", 0]},
            "class_type": "SaveImage",
        },
    }

    return workflow


def queue_prompt(workflow):
    """Queue a prompt in ComfyUI"""
    try:
        response = requests.post(
            f"{COMFYUI_URL}/prompt", json={"prompt": workflow}, timeout=30
        )
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error queuing prompt: {response.status_code} - {response.text}")
            return None
    except requests.exceptions.Timeout:
        print("Timeout connecting to ComfyUI")
        return None
    except Exception as e:
        print(f"Error connecting to ComfyUI: {e}")
        return None


def wait_for_completion(prompt_id, timeout=600):
    """Wait for prompt completion with extended timeout"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get(f"{COMFYUI_URL}/history/{prompt_id}", timeout=10)
            if response.status_code == 200:
                history = response.json()
                if prompt_id in history:
                    return True
        except Exception as e:
            print(f"Error checking status: {e}")

        time.sleep(5)  # Check every 5 seconds

    return False


def check_comfyui_connection():
    """Verify ComfyUI is running and accessible"""
    try:
        response = requests.get(f"{COMFYUI_URL}/system_stats", timeout=10)
        if response.status_code == 200:
            stats = response.json()
            print(f"✅ ComfyUI connected successfully!")
            print(
                f"   Version: {stats.get('system', {}).get('comfyui_version', 'Unknown')}"
            )
            return True
        else:
            print(f"❌ ComfyUI returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to ComfyUI at {COMFYUI_URL}: {e}")
        print("Make sure ComfyUI is running and accessible")
        return False


def generate_yoga_images():
    """Generate all 50 yoga beach images"""
    print("🧘‍♀️ Starting generation of 50 yoga beach images...")
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🖥️  Target: {COMFYUI_URL}")

    # Check ComfyUI connection first
    if not check_comfyui_connection():
        return 0, 50

    successful = 0
    failed = 0
    generation_log = []
    start_time = time.time()

    for i, pose_info in enumerate(YOGA_POSES, 1):
        print(f"\n📸 Generating image {i}/50: {pose_info['name']}")
        print(f"   Pose: {pose_info['pose']}")

        # Create detailed prompt
        detailed_prompt = BASE_PROMPT.format(
            pose=pose_info["pose"], lighting=pose_info["lighting"]
        )
        detailed_prompt += f", {pose_info['angle']}"

        print(f"   Prompt: {detailed_prompt[:80]}...")

        # Create workflow with random seed for variety
        workflow = create_workflow(detailed_prompt, NEGATIVE_PROMPT)

        # Queue prompt
        result = queue_prompt(workflow)
        if result and "prompt_id" in result:
            prompt_id = result["prompt_id"]
            print(f"   ✅ Queued with ID: {prompt_id}")

            # Wait for completion
            print("   ⏳ Generating (this may take 2-4 minutes)...")
            if wait_for_completion(prompt_id, timeout=300):  # 5 minute timeout
                successful += 1
                print(f"   🎉 Successfully generated!")

                generation_log.append(
                    {
                        "index": i,
                        "name": pose_info["name"],
                        "pose": pose_info["pose"],
                        "prompt": detailed_prompt,
                        "prompt_id": prompt_id,
                        "status": "success",
                        "timestamp": datetime.now().isoformat(),
                    }
                )

                # Try to rename file to descriptive name
                try:
                    # Allow some time for file to be written
                    time.sleep(2)

                    # The file might be saved with different naming convention
                    output_dir = Path(
                        "/workspace/ComfyUI/output"
                    )  # Update path for remote server
                    if output_dir.exists():
                        # Find recent files that might match
                        recent_files = [
                            f
                            for f in output_dir.glob("yoga_beach_*.png")
                            if time.time() - f.stat().st_mtime < 60
                        ]
                        if recent_files:
                            # Get the most recent file
                            latest_file = max(
                                recent_files, key=lambda f: f.stat().st_mtime
                            )
                            new_name = f"yoga_beach_{pose_info['name']}_{i:03d}.png"
                            new_path = output_dir / new_name
                            latest_file.rename(new_path)
                            print(f"   📁 Renamed to: {new_name}")
                        else:
                            print("   📁 File saved with default naming")
                    else:
                        print("   📁 Output directory not accessible for renaming")

                except Exception as e:
                    print(f"   ⚠️  Could not rename file: {e}")

            else:
                failed += 1
                print(f"   ❌ Generation failed or timed out")
                generation_log.append(
                    {
                        "index": i,
                        "name": pose_info["name"],
                        "pose": pose_info["pose"],
                        "prompt": detailed_prompt,
                        "prompt_id": prompt_id,
                        "status": "timeout",
                        "timestamp": datetime.now().isoformat(),
                    }
                )
        else:
            failed += 1
            print(f"   ❌ Failed to queue prompt")
            generation_log.append(
                {
                    "index": i,
                    "name": pose_info["name"],
                    "pose": pose_info["pose"],
                    "prompt": detailed_prompt,
                    "prompt_id": None,
                    "status": "failed_to_queue",
                    "timestamp": datetime.now().isoformat(),
                }
            )

        # Progress update every 10 images
        if i % 10 == 0:
            elapsed = time.time() - start_time
            avg_time = elapsed / i
            remaining = (50 - i) * avg_time
            print(
                f"\n📊 Progress: {i}/50 completed ({successful} successful, {failed} failed)"
            )
            print(f"⏱️  Average time per image: {avg_time:.1f}s")
            print(f"⏱️  Estimated time remaining: {remaining/60:.1f} minutes")

    # Save generation log
    log_data = {
        "timestamp": datetime.now().isoformat(),
        "total_requested": len(YOGA_POSES),
        "successful": successful,
        "failed": failed,
        "total_time_minutes": (time.time() - start_time) / 60,
        "average_time_per_image": (time.time() - start_time) / len(YOGA_POSES),
        "comfyui_url": COMFYUI_URL,
        "images": generation_log,
    }

    # Save log to local directory (accessible)
    log_path = Path("yoga_beach_generation_log.json")
    with open(log_path, "w") as f:
        json.dump(log_data, f, indent=2)

    print(f"\n🎉 Generation complete!")
    print(f"✅ Successfully generated: {successful}")
    print(f"❌ Failed: {failed}")
    print(f"⏱️  Total time: {(time.time() - start_time)/60:.1f} minutes")
    print(f"📝 Log saved to: {log_path.absolute()}")

    if successful > 0:
        print(f"\n🖼️  Generated images should be available in ComfyUI output directory")
        print(f"   Check: /workspace/ComfyUI/output/ on the server")

    return successful, failed


if __name__ == "__main__":
    print("🚀 Starting Yoga Beach Image Generation")
    print("=" * 50)

    # Run generation
    success_count, fail_count = generate_yoga_images()

    print("\n" + "=" * 50)
    print(f"🏁 Final Results: {success_count} successful, {fail_count} failed")

    if success_count >= 40:
        print("🎉 Excellent results! Most images generated successfully.")
    elif success_count >= 25:
        print("👍 Good results! Majority of images generated.")
    else:
        print("⚠️  Consider checking ComfyUI setup and retrying failed images.")
