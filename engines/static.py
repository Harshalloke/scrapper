import requests
from services.data_manager import load_config

def fetch_static(url: str) -> str:
    config = load_config()
    headers = {
        "User-Agent": config.get("user_agent")
    }
    
    r = requests.get(url, headers=headers, timeout=config.get("timeout", 10))
    r.raise_for_status()
    
    # Ensure we use the correct encoding
    if r.encoding is None or r.encoding == 'ISO-8859-1':
        r.encoding = r.apparent_encoding
        
    return r.text
