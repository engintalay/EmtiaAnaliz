import requests
import pandas as pd
import io

COINGECKO_BASE = "https://api.coingecko.com/api/v3"

# Bilinen kripto sembol → CoinGecko coin id eşlemesi
CRYPTO_IDS = {
    "BTC": "bitcoin", "ETH": "ethereum", "BNB": "binancecoin",
    "SOL": "solana",  "XRP": "ripple",   "DOGE": "dogecoin",
    "ADA": "cardano", "AVAX": "avalanche-2", "DOT": "polkadot",
    "MATIC": "matic-network", "LTC": "litecoin", "LINK": "chainlink",
    "UNI": "uniswap", "ATOM": "cosmos",  "TRX": "tron",
}

# Yahoo Finance sembol eşlemesi (emtia/endeks)
YAHOO_MAP = {
    "GOLD": "GC=F", "ALTIN": "GC=F",
    "OIL": "CL=F",  "PETROL": "CL=F", "BRENT": "BZ=F",
    "SILVER": "SI=F", "GUMUS": "SI=F",
    "NASDAQ": "^IXIC", "SP500": "^GSPC", "BIST100": "XU100.IS",
}


def fetch_crypto(coin_id: str, days: int = 90) -> pd.DataFrame:
    url = f"{COINGECKO_BASE}/coins/{coin_id}/market_chart"
    params = {"vs_currency": "usd", "days": days, "interval": "daily"}
    r = requests.get(url, params=params, timeout=15)
    r.raise_for_status()
    data = r.json()
    prices  = data["prices"]
    volumes = {v[0]: v[1] for v in data["total_volumes"]}
    df = pd.DataFrame(prices, columns=["timestamp", "close"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    df.set_index("timestamp", inplace=True)
    df["volume"] = df.index.map(lambda t: volumes.get(int(t.timestamp() * 1000), 0))
    df["open"]   = df["close"].shift(1).fillna(df["close"])
    df["high"]   = df["close"] * 1.01
    df["low"]    = df["close"] * 0.99
    return df[["open", "high", "low", "close", "volume"]]


def fetch_yfinance(symbol: str, period: str = "3mo") -> pd.DataFrame:
    import yfinance as yf
    ticker = yf.Ticker(symbol)
    df = ticker.history(period=period)
    if df.empty:
        return pd.DataFrame()
    df.index = pd.to_datetime(df.index)
    df.columns = [c.lower() for c in df.columns]
    return df[["open", "high", "low", "close", "volume"]]


def fetch_from_csv(content: bytes) -> pd.DataFrame:
    df = pd.read_csv(io.BytesIO(content))
    df.columns = [c.lower().strip() for c in df.columns]
    date_col = next((c for c in df.columns if "date" in c or "time" in c), None)
    if date_col:
        df[date_col] = pd.to_datetime(df[date_col])
        df.set_index(date_col, inplace=True)
    return df


def fetch_data(symbol: str, asset_type: str = "auto") -> pd.DataFrame:
    symbol = symbol.upper().strip()

    # Takma ad çözümle
    symbol = YAHOO_MAP.get(symbol, symbol)

    # Kripto mu?
    coin_id = CRYPTO_IDS.get(symbol)
    is_crypto = asset_type == "crypto" or (asset_type == "auto" and coin_id is not None)

    if is_crypto and coin_id:
        try:
            return fetch_crypto(coin_id)
        except Exception:
            pass  # fallback

    # yfinance dene
    for sym in [symbol, symbol + "-USD", symbol + ".IS"]:
        try:
            df = fetch_yfinance(sym)
            if not df.empty:
                return df
        except Exception:
            continue

    return pd.DataFrame()
