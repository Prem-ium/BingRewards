#!/bin/bash
rm /tmp/.X99-lock
echo "Starting X virtual framebuffer (Xvfb) in background..."
Xvfb -ac :99 -screen 0 1280x1024x16 &
export DISPLAY=:99
echo "BROWSER: $BROWSER"
echo "HANDLE_DRIVER: $HANDLE_DRIVER"
echo "Starting Bing Rewards Bot..."
python3 main.py