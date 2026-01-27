#!/bin/bash

# Enable Wi-Fi proxy
sudo networksetup -setwebproxy "Wi-Fi" 127.0.0.1 8383
sudo networksetup -setsecurewebproxy "Wi-Fi" 127.0.0.1 8383

# Start mitmdump
PY_SCRIPT="/Users/acyuan/Documents/Coding/filtererer/traffic_control.py"
nohup /opt/homebrew/bin/mitmdump -s "$PY_SCRIPT" --listen-port 8383 > /tmp/mitmdump.log 2>&1 &

echo "Proxy started on port 8383"
