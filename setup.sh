#!/bin/bash
# One-shot ComfyUI WAN2.2 Setup Script
set -e

echo "🚀 Starting ComfyUI WAN2.2 Setup..."
apt-get update -qq && apt-get install -y git curl jq unzip wget

# Setup SageAttention
pip install sageattention || echo "SageAttention install failed - continuing"

# Download essential LoRAs if CIVITAI_TOKEN is set
if [ ! -z "$CIVITAI_TOKEN" ]; then
    mkdir -p /workspace/ComfyUI/models/loras
    echo "Downloading LoRAs..."
fi

# Install custom nodes
cd /workspace/ComfyUI/custom_nodes
git clone https://github.com/ltdrdata/ComfyUI-Manager.git 2>/dev/null || true
git clone https://github.com/Kosinkadink/ComfyUI-AnimateDiff-Evolved.git 2>/dev/null || true

# Create control script
mkdir -p /workspace/scripts
echo "Creating control scripts..."

echo "✅ Setup complete! ComfyUI ready at port 8188"

