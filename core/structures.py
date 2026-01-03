from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin


def extract_tables(soup: BeautifulSoup) -> list:
    tables = []

    for table in soup.find_all("table"):
        rows = []
        headers = []

        thead = table.find("thead")
        if thead:
            headers = [th.get_text(strip=True) for th in thead.find_all("th")]

        tbody = table.find("tbody") or table
        for tr in tbody.find_all("tr"):
            cells = [td.get_text(strip=True) for td in tr.find_all(["td", "th"])]
            if cells:
                rows.append(cells)

        if rows:
            tables.append({
                "headers": headers,
                "rows": rows
            })

    return tables


def extract_lists(soup: BeautifulSoup) -> list:
    lists = []

    for ul in soup.find_all(["ul", "ol"]):
        items = [li.get_text(strip=True) for li in ul.find_all("li")]
        if len(items) > 1:
            lists.append(items)

    return lists


def extract_links(soup: BeautifulSoup, base_url: str) -> dict:
    internal = []
    external = []

    base_domain = urlparse(base_url).netloc

    for a in soup.find_all("a", href=True):
        href = urljoin(base_url, a["href"])
        domain = urlparse(href).netloc

        if domain == base_domain:
            internal.append(href)
        else:
            external.append(href)

    return {
        "internal": list(set(internal)),
        "external": list(set(external))
    }


def extract_images(soup: BeautifulSoup, base_url: str) -> list:
    images = []

    for img in soup.find_all("img", src=True):
        images.append({
            "src": urljoin(base_url, img["src"]),
            "alt": img.get("alt", "").strip()
        })

    return images
