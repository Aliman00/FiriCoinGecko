import json
import requests

def get_nok_to_usd_rate():
    try:
        return requests.get("https://open.er-api.com/v6/latest/NOK", timeout=5).json().get("rates", {}).get("USD", 0)
    except Exception:
        return 0

def load_previous_last(price_file):
    try:
        with open(price_file, "r") as file:
            return json.load(file).get("last", 0)
    except FileNotFoundError:
        return 0

def save_latest_prices(price_file, latest):
    with open(price_file, "w") as file:
        json.dump(latest, file, indent=4)
