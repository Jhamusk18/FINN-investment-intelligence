import httpx
from .config import USER_AGENT

HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept-Language": "en-US,en;q=0.9",
}

client = httpx.Client(headers=HEADERS, timeout=httpx.Timeout(25.0, connect=10.0), follow_redirects=True)
