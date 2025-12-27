from mitmproxy import http

# Sites to block completely
BLOCKED_HOSTS = ["instagram.com", "x.com", "twitter.com"]
# Redirect target
REDIRECT = "https://google.com"

class Blocker:
    def request(self, flow: http.HTTPFlow) -> None:
        host = flow.request.pretty_host
        path = flow.request.path

        # Check for blocked hosts or the specific YouTube Shorts path
        is_blocked_host = any(host == b or host.endswith("." + b) for b in BLOCKED_HOSTS)
        is_yt_shorts = (host in ["www.youtube.com", "youtube.com"]) and path.startswith("/shorts")

        if is_blocked_host or is_yt_shorts:
            flow.response = http.Response.make(
                302,
                b"",
                {"Location": REDIRECT}
            )

addons = [Blocker()]