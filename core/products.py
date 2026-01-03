from urllib.parse import urljoin

def extract_books(soup, base_url=""):
    books = []

    for book in soup.select("article.product_pod"):
        try:
            link_tag = book.h3.a
            title = link_tag["title"]
            href = link_tag["href"]
            url = urljoin(base_url, href)
            
            price = book.select_one(".price_color").text.strip()
            rating = book.p["class"][1]  # e.g. "Three"

            books.append({
                "title": title,
                "price": price,
                "rating": rating,
                "url": url
            })
        except:
            continue

    return books
