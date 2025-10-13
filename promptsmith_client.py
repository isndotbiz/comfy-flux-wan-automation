#!/usr/bin/env python3
import requests
import json
import sys
import os

# Multiple potential endpoints to try
ENDPOINTS = [
    "http://127.0.0.1:11434",  # Default Ollama local
    "http://localhost:11434",  # Localhost Ollama
    "http://10.0.0.100:8080",  # Original specified endpoint
    "http://127.0.0.1:8080",  # Local on 8080
]


def test_endpoint(url):
    """Test if an endpoint is reachable"""
    try:
        response = requests.get(f"{url}/api/tags", timeout=5)
        return response.status_code == 200
    except:
        return False


def find_working_endpoint():
    """Find the first working Ollama endpoint"""
    for endpoint in ENDPOINTS:
        print(f"🔍 Trying {endpoint}...")
        if test_endpoint(endpoint):
            print(f"✅ Found working endpoint: {endpoint}")
            return endpoint
    return None


def expand_prompt_ollama(base_prompt, endpoint, max_tokens=300):
    """Expand prompt using Ollama API"""
    url = f"{endpoint}/api/generate"
    payload = {
        "model": "llama3.1:8b",  # Adjust model name as needed
        "prompt": f"Transform this into a detailed, creative image generation prompt. Focus on visual details, lighting, composition, and artistic style. Keep it under 150 words:\n\n{base_prompt}\n\nDetailed prompt:",
        "stream": False,
        "options": {
            "temperature": 0.85,
            "top_p": 0.92,
            "repeat_penalty": 1.08,
            "num_predict": max_tokens,
        },
    }

    try:
        response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status()
        result = response.json()
        return result.get("response", "").strip()
    except Exception as e:
        print(f"❌ Ollama error: {e}")
        return None


def expand_prompt_llamacpp(base_prompt, endpoint, max_tokens=300):
    """Expand prompt using llama.cpp server API"""
    url = f"{endpoint}/completion"
    payload = {
        "prompt": f"Transform this into a detailed image prompt: {base_prompt}",
        "temperature": 0.85,
        "top_p": 0.92,
        "repeat_penalty": 1.08,
        "n_predict": max_tokens,
        "stop": ["\\n\\n", "User:", "### ", "Transform this"],
        "stream": False,
    }

    try:
        response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status()
        result = response.json()
        return result.get("content", "").strip()
    except Exception as e:
        print(f"❌ llama.cpp error: {e}")
        return None


def expand_prompt_fallback(base_prompt):
    """Simple fallback prompt expansion without AI"""
    styles = [
        "masterpiece, best quality, highly detailed",
        "photorealistic, 8K resolution, professional photography",
        "cinematic lighting, dramatic composition",
        "vibrant colors, sharp focus, intricate details",
    ]

    import random

    style = random.choice(styles)
    return f"{base_prompt}, {style}"


def expand_prompt(base_prompt, max_tokens=300):
    """Main function to expand prompts with fallbacks"""

    # Try to find working endpoint
    endpoint = find_working_endpoint()

    if endpoint:
        # Try Ollama API first
        result = expand_prompt_ollama(base_prompt, endpoint, max_tokens)
        if result:
            return result

        # Try llama.cpp API format
        result = expand_prompt_llamacpp(base_prompt, endpoint, max_tokens)
        if result:
            return result

    # Fallback to simple expansion
    print("🔄 Using fallback prompt expansion...")
    return expand_prompt_fallback(base_prompt)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python promptsmith_client.py 'your prompt here'")
        print("       python promptsmith_client.py --test  # Test connectivity")
        sys.exit(1)

    if sys.argv[1] == "--test":
        print("🧪 Testing PromptSmith connectivity...")
        endpoint = find_working_endpoint()
        if endpoint:
            print(f"✅ Ready to use {endpoint}")
        else:
            print("❌ No working endpoints found, will use fallback")
        sys.exit(0)

    prompt = " ".join(sys.argv[1:])
    print(f"📝 Original: {prompt}")

    expanded = expand_prompt(prompt)
    if expanded:
        print("\n✨ Expanded prompt:")
        print("─" * 60)
        print(expanded)
        print("─" * 60)
    else:
        print("❌ Failed to expand prompt")
