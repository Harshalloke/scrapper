from bs4 import BeautifulSoup

REMOVE_TAGS = [
    "script", "style", "noscript", "iframe",
    "header", "footer", "nav", "aside"
]


def clean_html(html: str) -> BeautifulSoup:
    soup = BeautifulSoup(html, "lxml")

    for tag in REMOVE_TAGS:
        for el in soup.find_all(tag):
            el.decompose()

    return soup


def clean_text(text: str) -> str:
    lines = [line.strip() for line in text.splitlines()]
    lines = [line for line in lines if len(line) > 5]  # remove only very short junk lines
    return "\n\n".join(lines)
