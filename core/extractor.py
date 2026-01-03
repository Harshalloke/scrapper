from readability import Document
from bs4 import BeautifulSoup
from core.cleaner import clean_html, clean_text


def extract_metadata(soup: BeautifulSoup) -> dict:
    title = soup.title.string.strip() if soup.title else ""

    description = ""
    meta = soup.find("meta", attrs={"name": "description"})
    if meta and meta.get("content"):
        description = meta["content"].strip()

    return {
        "title": title,
        "description": description
    }


def extract_headings(soup: BeautifulSoup) -> dict:
    headings = {}

    for level in range(1, 7):
        tag = f"h{level}"
        headings[tag] = [
            h.get_text(strip=True)
            for h in soup.find_all(tag)
        ]

    return headings


def extract_main_content(html: str) -> str:
    doc = Document(html)
    content_html = doc.summary(html_partial=True)

    soup = clean_html(content_html)
    text = soup.get_text(separator="\n")

    return clean_text(text)
