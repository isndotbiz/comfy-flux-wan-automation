"""
Centralized configuration and secrets management
Uses ~/Workspaces/secrets.env for credentials
"""

from dotenv import load_dotenv
import os

# Load secrets from centralized location
load_dotenv(dotenv_path=os.path.expanduser("~/Workspaces/secrets.env"))

# API Configuration
CIVITAI_TOKEN = os.environ.get("CIVITAI_TOKEN", os.environ.get("HF_TOKEN", ""))
HF_TOKEN = os.environ.get("HF_TOKEN", "")
HUGGINGFACE_TOKEN = os.environ.get("HUGGINGFACE_TOKEN", "")

# AI/ML APIs
REPLICATE_API = os.environ.get("REPLICATE_API", "")
FAL_API = os.environ.get("FAL_API", "")
RUNWAY_API = os.environ.get("RUNWAY_API", "")

# LLM APIs
OPENAI_API = os.environ.get("OPENAI_API", "")
ANTHROPIC_API = os.environ.get("ANTHROPIC_API", "")
OPENROUTER_API = os.environ.get("OPENROUTER_API", "")

# ComfyUI Configuration
COMFYUI_URL = os.environ.get("COMFYUI_URL", "http://127.0.0.1:8188")

# Ollama Configuration
OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "localhost")
OLLAMA_PORT = os.environ.get("OLLAMA_PORT", "11434")


def verify_secrets():
    """Verify that essential secrets are loaded"""
    missing = []
    if not HF_TOKEN:
        missing.append("HF_TOKEN")
    if not CIVITAI_TOKEN:
        missing.append("CIVITAI_TOKEN")

    if missing:
        print(f"⚠️  Missing required secrets: {', '.join(missing)}")
        print("Make sure ~/Workspaces/secrets.env exists and is properly formatted")
        return False

    print(f"✅ Secrets loaded successfully!")
    print(f"   HF_TOKEN: {HF_TOKEN[:10]}...")
    return True


if __name__ == "__main__":
    verify_secrets()
