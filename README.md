# ComfyUI Flux WAN2.2 Automation

Automated setup for ComfyUI with Flux and WAN2.2 models on RunPod.

## Quick Start

```bash
git clone https://github.com/YOUR_USERNAME/comfy-flux-wan-automation.git
cd comfy-flux-wan-automation
./setup.sh
```

## Commands

- `./scripts/comfy-ctl.sh start` - Start ComfyUI
- `./scripts/comfy-ctl.sh status` - Check status
- `./scripts/lora-manager.sh download 123456` - Download LoRA

## Environment Variables

- `CIVITAI_TOKEN` - Your CivitAI API token for LoRA downloads

## Access

ComfyUI will be available at: http://your-pod-url:8188

