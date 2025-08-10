import requests

class FiriClient:
    BASE_URL = "https://api.firi.com/v2/markets/{market_id}"
    SPREAD_URL = "https://api.firi.com/v2/markets/{market_id}/ticker"

    def get_market(self, market_id: str) -> dict:
        url = self.BASE_URL.format(market_id=market_id)
        try:
            return requests.get(url, timeout=5).json()
        except Exception as e:
            return {"error": str(e)}

    def get_spread(self, market_id: str) -> dict:
        url = self.SPREAD_URL.format(market_id=market_id)
        try:
            return requests.get(url, timeout=5).json()
        except Exception as e:
            return {"error": str(e)}

class CoinGeckoClient:
    def get_usd_price(self, coingecko_id: str):
        try:
            url = f"https://api.coingecko.com/api/v3/simple/price?ids={coingecko_id}&vs_currencies=usd"
            return requests.get(url, timeout=5).json().get(coingecko_id, {}).get("usd", None)
        except Exception:
            return None
