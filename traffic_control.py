from mitmproxy import http
from datetime import datetime

# Sites to block completely
BLOCKED_HOSTS = ["instagram.com", "x.com", "twitter.com"]

TIME_SENSITIVE_HOSTS = ["youtube.com"]
# between 9:30pm and 8:00am
TIME_CUTOFF_START = 21 * 60 + 30
TIME_CUTOFF_END = 8 * 60 + 00

# Redirect target
REDIRECT = "https://google.com"

class Blocker:
    def request(self, flow: http.HTTPFlow) -> None:
	host = flow.request.pretty_host
        path = flow.request.path

        # Check for blocked hosts or the specific YouTube Shorts path
        is_blocked_host = any(host == b or host.endswith("." + b) for b in BLOCKED_HOSTS)
        is_yt_shorts = (host in ["www.youtube.com", "youtube.com"]) and path.startswith("/shorts")

        # time sensitive blocking
        now = datetime.now()
        now_minutes = now.hour * 60 + now.minute

        too_late = now_minutes >= TIME_CUTOFF_START
        too_early = now_minutes < TIME_CUTOFF_END

        is_time_sensitive_blocked = (too_late or too_early) and any(host == b or host.endswith("." + b) for b in TIME_SENSITIVE_HOSTS)

        if is_blocked_host or is_yt_shorts or is_time_sensitive_blocked:
            flow.response = http.Response.make(
                302,
                b"",
                {"Location": REDIRECT}
            )

addons = [Blocker()]
