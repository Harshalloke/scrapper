from playwright.sync_api import sync_playwright


def fetch_dynamic(url: str) -> str:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        page.goto(url, timeout=30000)
        page.wait_for_load_state("networkidle")

        html = page.content()
        browser.close()

        return html
