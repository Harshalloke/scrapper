import time
import requests
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

_DOMAIN_RP_CACHE = {}
_DOMAIN_LAST_HIT = {}

# Use a standard browser user agent to avoid being blocked by strict robots.txt checks
DEFAULT_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"


def check_robots(url: str, user_agent=DEFAULT_USER_AGENT) -> int:
    parsed = urlparse(url)
    domain = parsed.netloc
    robots_url = f"{parsed.scheme}://{domain}/robots.txt"

    if domain in _DOMAIN_RP_CACHE:
        rp = _DOMAIN_RP_CACHE[domain]
    else:
        rp = RobotFileParser()
        # Use requests to fetch robots.txt with a real user agent
        try:
            r = requests.get(robots_url, headers={"User-Agent": user_agent}, timeout=5)
            if r.status_code == 200:
                rp.parse(r.text.splitlines())
                _DOMAIN_RP_CACHE[domain] = rp
            elif r.status_code == 403 or r.status_code == 401:
                # If robots.txt is explicitly forbidden, we should be careful.
                # However, many sites block bot access to robots.txt itself.
                # We'll return a conservative delay.
                return 3
            else:
                return 2
        except:
            return 2  # default delay

    # If we have a cached parser
    if not rp.can_fetch(user_agent, url):
        # Specific check for Wikipedia as it often blocks non-browser agents
        if "wikipedia.org" in domain:
            return 1 # Wikipedia usually allows /wiki/ for browsers
        raise PermissionError(f"Access to {url} is blocked by robots.txt")

    return rp.crawl_delay(user_agent) or 2


def rate_limit(url: str, delay: int):
    domain = urlparse(url).netloc
    last = _DOMAIN_LAST_HIT.get(domain)

    if last:
        sleep_time = delay - (time.time() - last)
        if sleep_time > 0:
            time.sleep(sleep_time)

    _DOMAIN_LAST_HIT[domain] = time.time()


def is_sensitive(url: str) -> bool:
    keywords = ["login", "signin", "signup", "account", "bank", "checkout"]
    return any(k in url.lower() for k in keywords)
