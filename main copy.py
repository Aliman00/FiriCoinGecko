from client import FiriClient, CoinGeckoClient
from utils import get_nok_to_usd_rate, load_previous_last, save_latest_prices

def crypto_price(ticker):
    ticker = ticker.upper()
    coingecko_map = {
        "ETH": "ethereum",
        "BTC": "bitcoin"
    }
    firi_market = f"{ticker}NOK"
    coingecko_id = coingecko_map.get(ticker) or ticker.lower()

    firi = FiriClient()
    coingecko = CoinGeckoClient()

    # Get Firi data
    latest = firi.get_market(firi_market)
    firi_raw_spread = firi.get_spread(firi_market)

    # Get CoinGecko USD price
    coinGecko = coingecko.get_usd_price(coingecko_id)

    # Get NOK → USD rate
    nok_to_usd = get_nok_to_usd_rate()

    # Load previous saved prices
    price_file = f"{ticker.lower()}Price.json"
    previous_last = load_previous_last(price_file)

    # Parse latest values and keep only numeric
    latest = {k: float(v) for k, v in latest.items() if isinstance(v, str) and v.replace('.', '', 1).isdigit()}
    latest_last = latest.get('last', 0)

    # Compare prices between last time program was run and now
    if previous_last > latest_last:
        print(f"(CoinGecko) {ticker} price: {coinGecko} USD")
        print(f"(Firi) {ticker} has gone down: {previous_last - latest_last} NOK")
        print(f"(Firi) {ticker} pris i USD: {latest_last * nok_to_usd} USD")
        print(f"Forskjell mellom CoinGecko og Firi: {round(coinGecko - (latest_last * nok_to_usd)) if coinGecko else 'N/A'} USD")
        spread_val = firi_raw_spread.get('spread', 0)
        try:
            spread_float = float(spread_val)
        except (ValueError, TypeError):
            spread_float = 0
        try:
            spread_int = int(float(spread_val))
        except (ValueError, TypeError):
            spread_int = spread_val
        print(f"Spread (difference between ask and bid): {spread_int} NOK")
        print(f"Spread % : {spread_float / latest_last * 100 if latest_last else 'N/A'}%")
    elif previous_last < latest_last:
        print(f"(CoinGecko) {ticker} price: {coinGecko} USD")
        print(f"(Firi) {ticker} has gone up: {latest_last - previous_last} NOK")
        print(f"(Firi) {ticker} pris i USD: {latest_last * nok_to_usd} USD")
        print(f"Forskjell mellom CoinGecko og Firi: {round(coinGecko - (latest_last * nok_to_usd)) if coinGecko else 'N/A'} USD")
        spread_val = firi_raw_spread.get('spread', 0)
        try:
            spread_float = float(spread_val)
        except (ValueError, TypeError):
            spread_float = 0
        try:
            spread_int = int(float(spread_val))
        except (ValueError, TypeError):
            spread_int = spread_val
        print(f"Spread (difference between ask and bid): {spread_int} NOK")
        print(f"Spread % : {spread_float / latest_last * 100 if latest_last else 'N/A'}%")
    else:
        print(f"(CoinGecko) {ticker} price: {coinGecko} USD")
        print(f"(Firi) {ticker} has not changed, it's still {latest_last} NOK")
        print(f"(Firi) {ticker} pris i USD: {latest_last * nok_to_usd} USD")
        print(f"Forskjell mellom CoinGecko og Firi: {round(coinGecko - (latest_last * nok_to_usd)) if coinGecko else 'N/A'} USD")
        spread_val = firi_raw_spread.get('spread', 0)
        try:
            spread_float = float(spread_val)
        except (ValueError, TypeError):
            spread_float = 0
        try:
            spread_int = int(float(spread_val))
        except (ValueError, TypeError):
            spread_int = spread_val
        print(f"Spread (difference between ask and bid): {spread_int} NOK")
        print(f"Spread % : {spread_float / latest_last * 100 if latest_last else 'N/A'}%")

    # Save latest prices locally
    save_latest_prices(price_file, latest)


if __name__ == "__main__":
    crypto_price("ETH")
    # print()
    # crypto_price("BTC")
