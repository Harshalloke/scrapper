from core.detector import needs_js
from core.cleaner import clean_html
from core.extractor import extract_main_content
from core.structures import extract_tables, extract_links, extract_images
from core.paginator import find_next_page
from core.ethics import check_robots, rate_limit, is_sensitive
from core.products import extract_books
from engines.static import fetch_static
from engines.dynamic import fetch_dynamic


def fetch_page(url: str) -> str:
    html = fetch_static(url)
    if needs_js(html):
        html = fetch_dynamic(url)
    return html


def scrape_service(
    url: str,
    mode: str = "auto",
    max_pages: int = 1
) -> dict:

    if is_sensitive(url):
        raise Exception("Sensitive URLs are blocked")

    delay = check_robots(url)

    page = 0
    current_url = url

    result = {
        "meta": {
            "start_url": url,
            "mode": mode,
            "pages_scraped": 0
        },
        "content": [],
        "products": [],
        "tables": [],
        "links": {
            "internal": [],
            "external": []
        },
        "images": []
    }

    while current_url and page < max_pages:
        page += 1
        rate_limit(current_url, delay)

        html = fetch_page(current_url)
        soup = clean_html(html)

        is_books = "books.toscrape.com" in current_url

        # ---- MODE DECISION ----
        if mode == "product" or (mode == "auto" and is_books):
            result["products"].extend(extract_books(soup))

        elif mode in ["article", "auto"]:
            result["content"].append(extract_main_content(html))

        if mode in ["auto", "tables"]:
            result["tables"].extend(extract_tables(soup))

        if mode in ["auto", "links"]:
            links = extract_links(soup, current_url)
            result["links"]["internal"].extend(links["internal"])
            result["links"]["external"].extend(links["external"])

        if mode in ["auto", "images"]:
            result["images"].extend(extract_images(soup, current_url))

        current_url = find_next_page(soup, current_url)

    result["meta"]["pages_scraped"] = page
    return result
