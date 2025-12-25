"""
This is the script to pass to mitmproxy.
"""

from mitmproxy import http

blocked_site_slugs = [
    "instagram.com",
    "x.com",
    "youtube.com/shorts"
]

class TrafficShaper:
    def request(self, flow: http.HTTPFlow) -> None:
        # Load slugs on every request to allow dynamic updates without restart
        
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