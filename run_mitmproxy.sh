#!/bin/bash

PY_SCRIPT="/Users/acyuan/Documents/Coding/filtererer/traffic_control.py"

# this script runs as me (acyuan)
nohup /opt/homebrew/bin/mitmdump -s "$PY_SCRIPT" --listen-port 8080 > /tmp/mitmdump.log 2>&1 &
