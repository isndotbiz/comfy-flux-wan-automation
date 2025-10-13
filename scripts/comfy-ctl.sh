#!/bin/bash
[ -f ~/Workspaces/secrets.env ] && source ~/Workspaces/secrets.env
# ComfyUI Control Script
PID_FILE=/tmp/comfyui.pid

case "$1" in
  start)
    if [ -f "$PID_FILE" ] && kill -0 $(cat "$PID_FILE") 2>/dev/null; then
      echo "ComfyUI already running"
    else
      echo "Starting ComfyUI..."
      cd /workspace/ComfyUI
      nohup python main.py --listen --use-sage-attention > /workspace/comfyui.log 2>&1 &
      echo $! > "$PID_FILE"
      echo "ComfyUI started"
    fi
    ;;
  stop)
    if [ -f "$PID_FILE" ]; then
      kill $(cat "$PID_FILE") 2>/dev/null && rm "$PID_FILE"
      echo "ComfyUI stopped"
    fi
    ;;
  status)
    if [ -f "$PID_FILE" ] && kill -0 $(cat "$PID_FILE") 2>/dev/null; then
      echo "ComfyUI running"
    else
      echo "ComfyUI not running"
    fi
    ;;
  *)
    echo "Usage: $0 {start|stop|status}"
    ;;
esac

