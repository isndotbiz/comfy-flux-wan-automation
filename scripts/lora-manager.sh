#!/bin/bash
# LoRA Manager for CivitAI
LORA_DIR="/workspace/ComfyUI/models/loras"

download_lora() {
    local model_id="$1"
    if [ -z "$CIVITAI_TOKEN" ]; then
        echo "ERROR: CIVITAI_TOKEN not set"
        return 1
    fi
    
    echo "Downloading LoRA ID: $model_id"
    model_info=$(curl -s -H "Authorization: Bearer $CIVITAI_TOKEN" \
        "https://civitai.com/api/v1/models/$model_id")
    
    download_url=$(echo "$model_info" | jq -r ".modelVersions[0].files[0].downloadUrl // empty")
    file_name=$(echo "$model_info" | jq -r ".modelVersions[0].files[0].name // \"model.safetensors\"")
    
    if [ -z "$download_url" ]; then
        echo "ERROR: No download URL found"
        return 1
    fi
    
    mkdir -p "$LORA_DIR"
    wget -q --show-progress \
         --header="Authorization: Bearer $CIVITAI_TOKEN" \
         -O "$LORA_DIR/$file_name" \
         "$download_url"
    
    echo "Downloaded: $file_name"
}

case "$1" in
    download)
        IFS="," read -ra LORA_IDS <<< "$2"
        for id in "${LORA_IDS[@]}"; do
            download_lora "$id"
        done
        ;;
    *)
        echo "Usage: $0 download MODEL_ID[,MODEL_ID,...]"
        ;;
esac

