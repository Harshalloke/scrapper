def needs_js(html: str) -> bool:
    signals = [
        "id=\"__next\"",
        "id=\"root\"",
        "window.__INITIAL_STATE__",
        "data-reactroot"
    ]

    return any(signal in html for signal in signals)
