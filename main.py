
import streamlit as st
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

    # Save latest prices locally
    save_latest_prices(price_file, latest)

    # Prepare results for display
    result = {}
    result['CoinGecko USD'] = coinGecko
    result['Firi last NOK'] = latest_last
    result['Firi last USD'] = latest_last * nok_to_usd
    result['NOK→USD rate'] = nok_to_usd
    result['Previous last NOK'] = previous_last
    # Add Firi ask and bid if available
    result['Asking'] = None
    result['Bid'] = None
    if isinstance(firi_raw_spread, dict):
        ask = firi_raw_spread.get('ask')
        bid = firi_raw_spread.get('bid')
        try:
            result['Asking'] = float(ask) if ask is not None else None
        except (ValueError, TypeError):
            result['Asking'] = None
        try:
            result['Bid'] = float(bid) if bid is not None else None
        except (ValueError, TypeError):
            result['Bid'] = None
    result['Spread'] = firi_raw_spread.get('spread', 0)
    try:
        spread_float = float(result['Spread'])
    except (ValueError, TypeError):
        spread_float = 0
    result['Spread %'] = spread_float / latest_last * 100 if latest_last else 'N/A'
    if previous_last > latest_last:
        result['Change'] = f"Down {previous_last - latest_last} NOK"
    elif previous_last < latest_last:
        result['Change'] = f"Up {latest_last - previous_last} NOK"
    else:
        result['Change'] = "No change"
    if coinGecko is not None:
        result['Diff CoinGecko-Firi USD'] = round(coinGecko - (latest_last * nok_to_usd), 2)
    else:
        result['Diff CoinGecko-Firi USD'] = 'N/A'
    return result


def main():
    st.set_page_config(page_title="Crypto Price Tracker", page_icon="💸", layout="centered")
    st.title("💸 Crypto Price Tracker (Firi & CoinGecko)")
    st.caption("Live price, spread, and comparison between Firi and CoinGecko.")


    ticker = st.selectbox("Select ticker", ["ETH", "BTC"])
    # Helper to format as float or N/A
    def fmt_float(val):
        try:
            return f"{float(val):.2f}"
        except (ValueError, TypeError):
            return "N/A"
    def fmt_percent(val):
        try:
            return f"{float(val):.2f}%"
        except (ValueError, TypeError):
            return "N/A"

    # Use session state to persist result
    if 'result' not in st.session_state:
        st.session_state['result'] = None
    get_price_clicked = st.button("Get Price Info", key="get_price_btn")
    if get_price_clicked:
        st.session_state['result'] = crypto_price(ticker)

    result = st.session_state['result']
    if result:
        st.subheader("FIRI PRICE")
        st.markdown(f"<h1 style='font-size:2.5em; color:#27ae60; margin-bottom:0.2em'>{result['Firi last NOK']:.2f} NOK</h1>", unsafe_allow_html=True)
        st.caption(result['Change'])

        col1, col2, col3 = st.columns(3)
        col1.metric(
            label="Firi Asking Price (NOK) Seller",
            value=fmt_float(result.get('Asking'))
        )
        col2.metric(
            label="Firi Bid Price (NOK) Buyer",
            value=fmt_float(result.get('Bid'))
        )
        col3.metric(
            label="Firi Spread (NOK) Seller-Buyer",
            value=fmt_float(result.get('Spread')),
            delta=fmt_percent(result.get('Spread %'))
        )

        # Row: Firi USD, CoinGecko, Difference
        col4, col5, col6 = st.columns(3)
        col4.metric(
            label="Firi Price (USD)",
            value=f"{result['Firi last USD']:.2f}"
        )
        col5.metric(
            label="CoinGecko Price (USD)",
            value=f"{result['CoinGecko USD']:.2f}" if result['CoinGecko USD'] else "N/A"
        )
        col6.metric(
            label="Difference (USD)",
            value=f"{result['Diff CoinGecko-Firi USD']}" if result['Diff CoinGecko-Firi USD'] != 'N/A' else "N/A"
        )

        # Calculator: Compare proceeds from selling X crypto at Firi vs CoinGecko price
        st.subheader("Calculator")
        st.write("Calculate the difference in proceeds when selling a given amount of crypto at Firi vs CoinGecko price.")
        col7, col8 = st.columns(2)
        if 'sell_amount_crypto' not in st.session_state:
            st.session_state['sell_amount_crypto'] = 1.0
        with col7:
            sell_amount_crypto = st.number_input(
                f"Sell Amount ({ticker})", min_value=0.0, step=1.0, value=st.session_state['sell_amount_crypto'], key="sell_amount_crypto_input")
        with col8:
            pass

        calc_clicked = st.button("Calculate Difference", key="calc_btn")
        if calc_clicked:
            st.session_state['sell_amount_crypto'] = sell_amount_crypto
            firi_usd = result['Firi last USD']
            coingecko_usd = result['CoinGecko USD']
            if firi_usd and coingecko_usd:
                proceeds_firi = sell_amount_crypto * firi_usd
                proceeds_cg = sell_amount_crypto * coingecko_usd
                proceeds_ask = 1 * result['Asking'] if result['Asking'] is not None else None
                proceeds_bid = 1 * result['Bid'] if result['Bid'] is not None else None
                diff = proceeds_firi - proceeds_cg
                winner = "Firi" if diff > 0 else ("CoinGecko" if diff < 0 else "Same")

                st.markdown("""
                <style>
                .proceeds-box {
                    border-radius: 8px;
                    padding: 1em;
                    margin-bottom: 0.5em;
                    font-size: 1.2em;
                    color: #111 !important;
                }
                .winner {background: #e8ffe8; border: 2px solid #27ae60;}
                .loser {background: #ffeaea; border: 2px solid #c0392b;}
                .neutral {background: #f0f0f0; border: 2px solid #bbb;}
                </style>
                """, unsafe_allow_html=True)

                colA, colB = st.columns(2)
                with colA:
                    st.markdown(f"<div class='proceeds-box {'winner' if winner=='Firi' else 'loser' if winner=='CoinGecko' else 'neutral'}'>"
                                f"<b>Firi Market Price</b><br>"
                                f"<b>NOK:</b> {proceeds_firi / result['NOK→USD rate']:.2f}<br>"
                                f"<b>USD:</b> {proceeds_firi:.2f}"
                                "</div>", unsafe_allow_html=True)
                    if proceeds_ask is not None:
                        st.markdown(f"<div class='proceeds-box neutral'>"
                                    f"<b>Firi Ask Price</b><br>"
                                    f"<b>NOK:</b> {proceeds_ask:.2f}<br>"
                                    f"<b>USD:</b> {proceeds_ask * result['NOK→USD rate']:.2f}"
                                    "</div>", unsafe_allow_html=True)
                    if proceeds_bid is not None:
                        st.markdown(f"<div class='proceeds-box neutral'>"
                                    f"<b>Firi Bid Price</b><br>"
                                    f"<b>NOK:</b> {proceeds_bid:.2f}<br>"
                                    f"<b>USD:</b> {proceeds_bid * result['NOK→USD rate']:.2f}"
                                    "</div>", unsafe_allow_html=True)
                with colB:
                    st.markdown(f"<div class='proceeds-box {'winner' if winner=='CoinGecko' else 'loser' if winner=='Firi' else 'neutral'}'>"
                                f"<b>CoinGecko Price</b><br>"
                                f"<b>NOK:</b> {proceeds_cg / result['NOK→USD rate']:.2f}<br>"
                                f"<b>USD:</b> {proceeds_cg:.2f}"
                                "</div>", unsafe_allow_html=True)
                    st.markdown(f"<div class='proceeds-box neutral'>"
                                f"<b>CoinGecko USD Price</b><br>"
                                f"<b>NOK:</b> {coingecko_usd / result['NOK→USD rate']:.2f}<br>"
                                f"<b>USD:</b> {coingecko_usd:.2f}"
                                "</div>", unsafe_allow_html=True)
                    st.markdown(f"<div class='proceeds-box {'winner' if winner=='Same' else 'neutral'}'>"
                                f"<b>Difference</b><br>"
                                f"<b>NOK:</b> {abs(diff / result['NOK→USD rate']):.2f}<br>"
                                f"<b>USD:</b> {abs(diff):.2f}"
                                "</div>", unsafe_allow_html=True)

                if winner == "Same":
                    st.info("Both give the same proceeds.")
                else:
                    st.success(f"{winner} gives you {abs(diff):.2f} USD more for {sell_amount_crypto} {ticker}.")
                    st.success(f"That's {abs(diff / result['NOK→USD rate']):.2f} NOK more at the current NOK→USD rate.")
            else:
                st.write("Price data not available.")


if __name__ == "__main__":
    main()
