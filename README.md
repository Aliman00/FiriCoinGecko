# Firi Crypto Price Tracker

A simple Streamlit web app to track live cryptocurrency prices (ETH, BTC) from Firi and CoinGecko, compare spreads, and calculate proceeds from selling crypto.

## Features

- Live price and spread from Firi
- CoinGecko USD price comparison
- Difference calculator for selling crypto
- Simple, interactive UI

## Usage

### Local

1. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
2. Run the app:
    ```bash
    streamlit run main.py
    ```

### Docker

1. Build the image:
    ```bash
    docker build -t firi-tracker .
    ```
2. Run the container:
    ```bash
    docker run -p 8501:8501 firi-tracker
    ```

### Render.com

- Push this repo to GitHub.
- Create a new Web Service on Render.com.
- Use the following build and start commands:
    - **Build Command:** `pip install -r requirements.txt`
    - **Start Command:** `streamlit run main.py --server.port=10000 --server.address=0.0.0.0`

## Project Structure

```
Firi/
├── main.py
├── client.py
├── utils.py
├── requirements.txt
├── Dockerfile
├── .gitignore
├── .dockerignore
└── README.md
```

## License