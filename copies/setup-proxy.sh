#!/bin/bash

# Set proxy (runs as root via LaunchDaemon)
networksetup -setwebproxy "Wi-Fi" 127.0.0.1 8080
networksetup -setsecurewebproxy "Wi-Fi" 127.0.0.1 8080

# This was a bad name -- we are using mitmdump, not mitmproxy
su - acyuan -c "/Users/acyuan/Documents/Coding/filtererer/run_mitmproxy.sh"