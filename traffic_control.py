"""
This is the script to pass to mitmproxy.

Commands:
mitmdump -s traffic_control.py
# Set Web Proxy (HTTP)
sudo networksetup -setwebproxy "Wi-Fi" 127.0.0.1 8080
# Set Secure Web Proxy (HTTPS)
sudo networksetup -setsecurewebproxy "Wi-Fi" 127.0.0.1 8080
"""

from mitmproxy import http
import json
import os

# Configuration file path - relative to this script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(SCRIPT_DIR, "blocked_sites.json")

def load_blocked_slugs():
    """Loads blocked slugs from the JSON configuration file."""
    if not os.path.exists(CONFIG_FILE):
        return []
    try:
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading config: {e}")
        return []

class TrafficShaper:
    def request(self, flow: http.HTTPFlow) -> None:
        # Load slugs on every request to allow dynamic updates without restart
        blocked_site_slugs = load_blocked_slugs()
        
        # 1. Get the full URL
        url = flow.request.pretty_url

        if any([slug in url for slug in blocked_site_slugs]):
            print(f"DEBUG: Redirecting {url}")
            flow.request.host = "calendar.google.com"
            # Change path (everything after host)
            flow.request.path = ""

addons = [
    TrafficShaper()
]