from core.detector import needs_js
from core.cleaner import clean_html
from core.extractor import extract_main_content
from core.structures import extract_tables
from core.paginator import find_next_page
from core.ethics import check_robots, rate_limit, is_sensitive
from core.exporter import export_json, export_txt, export_markdown, export_tables_csv
from engines.static import fetch_static
from engines.dynamic import fetch_dynamic
from core.products import extract_books


def fetch(url):
    html = fetch_static(url)
    if needs_js(html):
        html = fetch_dynamic(url)
    return html


def main():
    start_url = input("URL: ").strip()
    max_pages = int(input("Max pages: ").strip())

    if is_sensitive(start_url):
        print("❌ Sensitive page blocked")
        return

    delay = check_robots(start_url)
    is_books_site = "books.toscrape.com" in start_url

    content_blocks = []
    tables = []
    page = 0
    url = start_url

    while url and page < max_pages:
        page += 1
        print(f"Scraping page {page}: {url}")

        rate_limit(url, delay)
        html = fetch(url)
        soup = clean_html(html)

        if is_books_site:
            books = extract_books(soup)
            content_blocks.extend(
                [f"{b['title']} | {b['price']} | {b['rating']}" for b in books]
            )
        else:
            content_blocks.append(extract_main_content(html))
            tables.extend(extract_tables(soup))

        next_url = find_next_page(soup, url)
        if not next_url:
            break

        url = next_url

    final_content = "\n\n".join(content_blocks)

    export_txt(final_content)
    export_markdown("Scraped Content", final_content)
    export_tables_csv(tables)
    export_json({
        "pages": page,
        "items": len(content_blocks)
    })

    print("✅ Done. Data exported.")


if __name__ == "__main__":
    main()
