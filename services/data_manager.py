import json
import os
import time
from datetime import datetime

# Check for persistent storage path (Render disk)
DATA_DIR = "/data" if os.path.exists("/data") else "."
STATS_FILE = os.path.join(DATA_DIR, "stats.json")
CONFIG_FILE = os.path.join(DATA_DIR, "config.json")

DEFAULT_CONFIG = {
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "default_mode": "auto",
    "proxy_enabled": False,
    "api_key": "wx_live_free_key_12345",
    "max_pages_limit": 10,
    "timeout": 30
}

def load_config():
    if not os.path.exists(CONFIG_FILE):
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG
    try:
        with open(CONFIG_FILE, "r") as f:
            return {**DEFAULT_CONFIG, **json.load(f)}
    except:
        return DEFAULT_CONFIG

def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)

def log_scrape(url, status, pages, duration, items=0):
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "url": url,
        "status": status,
        "pages": pages,
        "duration": round(duration, 2),
        "items": items
    }
    
    stats = []
    if os.path.exists(STATS_FILE):
        try:
            with open(STATS_FILE, "r") as f:
                stats = json.load(f)
        except:
            stats = []
            
    stats.append(log_entry)
    
    # Keep only last 1000 entries
    if len(stats) > 1000:
        stats = stats[-1000:]
        
    with open(STATS_FILE, "w") as f:
        json.dump(stats, f)

def get_analytics():
    if not os.path.exists(STATS_FILE):
        return None
        
    try:
        with open(STATS_FILE, "r") as f:
            stats = json.load(f)
    except:
        return None
        
    if not stats:
        return None
        
    total_requests = len(stats)
    successes = [s for s in stats if s["status"] == "success"]
    success_rate = (len(successes) / total_requests * 100) if total_requests > 0 else 0
    avg_duration = sum(s["duration"] for s in stats) / total_requests if total_requests > 0 else 0
    total_items = sum(s["items"] for s in stats)
    
    # Group by day for the chart
    history = {}
    for s in stats:
        day = s["timestamp"].split("T")[0]
        history[day] = history.get(day, 0) + 1
        
    # Format for UI
    sorted_history = [{"date": k, "count": v} for k, v in sorted(history.items(), reverse=True)[:7]]
    
    return {
        "total_requests": total_requests,
        "success_rate": f"{round(success_rate, 1)}%",
        "avg_time": f"{round(avg_duration, 2)}s",
        "data_extracted": f"{total_items} items",
        "history": sorted_history[::-1] # chronological for chart
    }
