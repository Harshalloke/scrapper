from flask import Flask, render_template, request, send_file, jsonify
from core.detector import needs_js
from core.cleaner import clean_html
from core.extractor import extract_main_content
from core.structures import extract_tables, extract_links, extract_images
from core.paginator import find_next_page
from core.ethics import check_robots, rate_limit, is_sensitive
from core.exporter import export_json, export_txt
from core.products import extract_books
from engines.static import fetch_static
from engines.dynamic import fetch_dynamic
from services.data_manager import log_scrape, get_analytics, load_config, save_config
import io
import zipfile
import requests
import time
import json

app = Flask(__name__)


def fetch(url):
    html = fetch_static(url)
    if needs_js(html):
        html = fetch_dynamic(url)
    return html


def scrape(url, max_pages=1, mode="auto"):
    start_time = time.time()
    if is_sensitive(url):
        log_scrape(url, "blocked", 0, time.time() - start_time)
        raise Exception("Sensitive pages are blocked")

    try:
        config = load_config()
        max_pages = min(max_pages, config.get("max_pages_limit", 10))
        
        delay = check_robots(url)
        page = 0
        current_url = url

        result = {
            "content": [],
            "products": [],
            "tables": [],
            "links": {"internal": [], "external": []},
            "images": [],
            "stats": {}
        }

        while current_url and page < max_pages:
            page += 1
            rate_limit(current_url, delay)

            html = fetch(current_url)
            soup = clean_html(html)

            is_books = "books.toscrape.com" in current_url

            if mode == "product" or (mode == "auto" and is_books):
                result["products"].extend(extract_books(soup, current_url))

            if mode in ["article", "auto"] and not is_books:
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

        item_count = len(result["content"]) + len(result["products"]) + len(result["tables"]) + len(result["images"])
        result["stats"] = {
            "pages": page,
            "articles": len(result["content"]),
            "products": len(result["products"]),
            "tables": len(result["tables"]),
            "images": len(result["images"])
        }
        
        log_scrape(url, "success", page, time.time() - start_time, item_count)
        return result
    except Exception as e:
        log_scrape(url, "error", 0, time.time() - start_time)
        raise e


@app.route("/")
def landing():
    return render_template("index.html", landing=True)


@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    data = None
    error = None

    if request.method == "POST":
        try:
            data = scrape(
                url=request.form["url"],
                max_pages=int(request.form["pages"]),
                mode=request.form["mode"]
            )
            # Export logic implementation
            export_json(data, "output.json")
            
            content_text = ""
            if data["content"]:
                content_text = "\n\n".join(data["content"])
            elif data["products"]:
                content_text = "\n".join([f"{p['title']} - {p['price']}" for p in data["products"]])
            
            export_txt(content_text, "output.txt")
        except Exception as e:
            error = str(e)

    return render_template("dashboard.html", data=data, error=error)


@app.route("/api-guide")
def api_guide():
    return render_template("api_guide.html")


@app.route("/analytics")
def analytics():
    stats = get_analytics()
    if not stats:
        # Fallback dummy data if no history yet
        stats = {
            "total_requests": 0,
            "success_rate": "0%",
            "avg_time": "0s",
            "data_extracted": "0 items",
            "history": []
        }
    return render_template("analytics.html", stats=stats)


@app.route("/settings", methods=["GET", "POST"])
def settings():
    if request.method == "POST":
        config = {
            "user_agent": request.form.get("user_agent"),
            "default_mode": request.form.get("default_mode"),
            "proxy_enabled": "proxy_enabled" in request.form,
            "api_key": request.form.get("api_key"),
            "max_pages_limit": int(request.form.get("max_pages_limit", 10)),
            "timeout": int(request.form.get("timeout", 30))
        }
        save_config(config)
        return render_template("settings.html", config=config, success=True)
        
    config = load_config()
    return render_template("settings.html", config=config)


@app.route("/download/txt")
def download_txt():
    return send_file("output.txt", as_attachment=True)


@app.route("/download/json")
def download_json():
    return send_file("output.json", as_attachment=True)


@app.route("/download/images")
def download_images():
    try:
        with open("output.json", "r") as f:
            data = json.load(f)
        
        images = data.get("images", [])
        if not images:
            return "No images found to download", 404

        memory_file = io.BytesIO()
        with zipfile.ZipFile(memory_file, 'w') as zf:
            for i, img in enumerate(images):
                try:
                    img_url = img['src']
                    response = requests.get(img_url, timeout=5, headers={"User-Agent": "Mozilla/5.0"})
                    if response.status_code == 200:
                        ext = img_url.split('.')[-1].split('?')[0]
                        if len(ext) > 4: ext = 'jpg'
                        zf.writestr(f"image_{i+1}.{ext}", response.content)
                except:
                    continue
        
        memory_file.seek(0)
        return send_file(
            memory_file,
            mimetype='application/zip',
            as_attachment=True,
            download_name='scraped_images.zip'
        )
    except Exception as e:
        return str(e), 500


@app.route("/api/scrape", methods=["POST"])
def api_scrape():
    config = load_config()
    provided_key = request.headers.get("X-API-Key")
    
    if provided_key != config.get("api_key"):
        return jsonify({"error": "Invalid or missing API key"}), 401
        
    payload = request.get_json()
    if not payload or "url" not in payload:
        return jsonify({"error": "Missing 'url' parameter"}), 400
    
    try:
        results = scrape(
            url=payload["url"],
            max_pages=int(payload.get("max_pages", 1)),
            mode=payload.get("mode", "auto")
        )
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/health")
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(debug=True)
