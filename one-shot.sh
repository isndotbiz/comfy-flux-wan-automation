#!/bin/bash
# ULTIMATE ONE-SHOT COMFYUI FLUX WAN2.2 SETUP
# curl -fsSL https://raw.githubusercontent.com/YOUR_USERNAME/comfy-flux-wan-automation/main/one-shot.sh | bash

set -e
cd /workspace

echo "🚀 ONE-SHOT COMFYUI FLUX WAN2.2 SETUP"
echo "======================================"

# Clone or update automation repo
if [ -d "comfy-flux-wan-automation" ]; then
    cd comfy-flux-wan-automation
    git pull 2>/dev/null || echo "Git pull failed, continuing..."
else
    git clone https://github.com/YOUR_USERNAME/comfy-flux-wan-automation.git 2>/dev/null || {
        echo "⚠️  Clone failed, creating local setup..."
        mkdir -p comfy-flux-wan-automation/{scripts,configs,workflows,logs}
        cd comfy-flux-wan-automation
    }
fi

# Run setup
if [ -f "setup.sh" ]; then
    ./setup.sh
else
    echo "⚠️  setup.sh not found, running basic setup..."
    apt-get update -qq && apt-get install -y git curl jq unzip wget
    pip install sageattention || echo "SageAttention install failed"
fi

# Ensure ComfyUI is running
if ! pgrep -f "ComfyUI.*main.py" > /dev/null; then
    echo "🚀 Starting ComfyUI..."
    cd /workspace/ComfyUI
    nohup python main.py --listen --use-sage-attention > /workspace/comfyui.log 2>&1 &
    sleep 10
fi

# Create shortcuts
echo "alias comfy-start=\"/workspace/comfy-flux-wan-automation/scripts/comfy-ctl.sh start\"" >> ~/.bashrc
echo "alias comfy-status=\"/workspace/comfy-flux-wan-automation/scripts/comfy-ctl.sh status\"" >> ~/.bashrc
echo "alias lora-dl=\"/workspace/comfy-flux-wan-automation/scripts/lora-manager.sh download\"" >> ~/.bashrc

echo ""
echo "✅ SETUP COMPLETE!"
echo "==================="
echo "🌐 ComfyUI: http://your-pod-url:8188"
echo "📁 Automation: /workspace/comfy-flux-wan-automation/"
echo ""
echo "Quick commands:"
echo "  comfy-start    # Start ComfyUI"
echo "  comfy-status   # Check status"
echo "  lora-dl 123456 # Download LoRA (needs CIVITAI_TOKEN)"
echo ""
echo "🎯 Ready to generate! Set CIVITAI_TOKEN for LoRA downloads."

