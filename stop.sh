#!/bin/bash

# Disable Wi-Fi proxy
sudo networksetup -setwebproxystate "Wi-Fi" off
sudo networksetup -setsecurewebproxystate "Wi-Fi" off

# Kill mitmdump
pkill -f mitmdump

echo "Proxy stopped"
