from bs4 import BeautifulSoup
from urllib.parse import urljoin


NEXT_KEYWORDS = ["next", "older", "›", "»", "next page", "forward", "continue"]


def find_next_page(soup: BeautifulSoup, base_url: str) -> str | None:
    # 1. Standard rel="next"
    link = soup.find("a", rel="next")
    if link and link.get("href"):
        return urljoin(base_url, link["href"])

    # 2. More precise keyword-based detection
    for a in soup.find_all("a", href=True):
        text = a.get_text(strip=True).lower()
        
        # Match exact word or common patterns
        if any(k == text or f" {k} " in f" {text} " for k in NEXT_KEYWORDS):
            return urljoin(base_url, a["href"])
        
        # Check classes or IDs for pagination hints
        classes = " ".join(a.get("class", [])).lower()
        if "next" in classes or "pagination-next" in classes:
            return urljoin(base_url, a["href"])

    return None
