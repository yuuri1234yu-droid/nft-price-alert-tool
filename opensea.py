import requests
import time

API_URL = "https://api.opensea.io/api/v2/collections"

def get_floor_price(collection_slug: str):
    try:
        r = requests.get(
            f"{API_URL}/{collection_slug}",
            timeout=10
        )
        data = r.json()
        return data["collection"]["stats"]["floor_price"]
    except Exception as e:
        print("OpenSea API error:", e)
        return None
