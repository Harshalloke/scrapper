from flask import Blueprint, request, jsonify
from services.scraper_service import scrape_service

api = Blueprint("api", __name__)


@api.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


@api.route("/api/scrape", methods=["POST"])
def scrape():
    data = request.get_json()

    url = data.get("url")
    mode = data.get("mode", "auto")
    max_pages = int(data.get("max_pages", 1))

    if not url:
        return jsonify({"error": "URL is required"}), 400

    try:
        result = scrape_service(
            url=url,
            mode=mode,
            max_pages=max_pages
        )
        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500
