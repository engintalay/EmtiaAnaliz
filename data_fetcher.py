import requests
import pandas as pd
import io

COINGECKO_BASE = "https://api.coingecko.com/api/v3"
YF_HEADERS = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"}

CRYPTO_IDS = {
    "BTC": "bitcoin", "ETH": "ethereum", "BNB": "binancecoin",
    "SOL": "solana",  "XRP": "ripple",   "DOGE": "dogecoin",
    "ADA": "cardano", "AVAX": "avalanche-2", "DOT": "polkadot",
    "MATIC": "matic-network", "LTC": "litecoin", "LINK": "chainlink",
    "UNI": "uniswap", "ATOM": "cosmos",  "TRX": "tron",
}

YAHOO_MAP = {
    "GOLD": "GC=F", "ALTIN": "GC=F",
    "OIL": "CL=F",  "PETROL": "CL=F", "BRENT": "BZ=F",
    "SILVER": "SI=F", "GUMUS": "SI=F",
    "NASDAQ": "^IXIC", "SP500": "^GSPC", "BIST100": "XU100.IS",
    "DOLAR": "USDTRY=X", "EURO": "EURTRY=X",
    "USDTRY": "USDTRY=X", "EURTRY": "EURTRY=X",
    "GBPTRY": "GBPTRY=X", "JPYTRY": "JPYTRY=X",
    "USDTTRY": "USDTTRY=X",
    "EURUSD": "EURUSD=X", "GBPUSD": "GBPUSD=X",
}

# Döviz çifti kalıpları: "USDT TRY", "USD/TRY", "BTC USD"
CURRENCY_PAIRS = {
    "USDT": "USDT", "USD": "USD", "EUR": "EUR", "GBP": "GBP",
    "JPY": "JPY", "TRY": "TRY", "CHF": "CHF", "AUD": "AUD",
}

# gün → Yahoo range/interval
def _yf_range(days: int) -> tuple:
    if days <= 30:   return "1mo",  "1d"
    if days <= 90:   return "3mo",  "1d"
    if days <= 180:  return "6mo",  "1d"
    if days <= 365:  return "1y",   "1d"
    return "2y", "1d"


def fetch_yf_api(symbol: str, days: int = 90) -> pd.DataFrame:
    """Yahoo Finance query API — yfinance kütüphanesi yerine direkt HTTP."""
    range_, interval = _yf_range(days)
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
    params = {"interval": interval, "range": range_}
    r = requests.get(url, params=params, headers=YF_HEADERS, timeout=15)
    r.raise_for_status()
    result = r.json()["chart"]["result"]
    if not result:
        return pd.DataFrame()
    data       = result[0]
    timestamps = data["timestamp"]
    q          = data["indicators"]["quote"][0]
    df = pd.DataFrame({
        "open":   q.get("open",   []),
        "high":   q.get("high",   []),
        "low":    q.get("low",    []),
        "close":  q.get("close",  []),
        "volume": q.get("volume", []),
    }, index=pd.to_datetime(timestamps, unit="s"))
    df.index.name = "date"
    return df.dropna(subset=["close"])


def fetch_crypto(coin_id: str, days: int = 90) -> pd.DataFrame:
    url = f"{COINGECKO_BASE}/coins/{coin_id}/market_chart"
    params = {"vs_currency": "usd", "days": days, "interval": "daily"}
    r = requests.get(url, params=params, timeout=15)
    r.raise_for_status()
    data    = r.json()
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


def fetch_from_csv(content: bytes) -> pd.DataFrame:
    df = pd.read_csv(io.BytesIO(content))
    df.columns = [c.lower().strip() for c in df.columns]
    date_col = next((c for c in df.columns if "date" in c or "time" in c), None)
    if date_col:
        df[date_col] = pd.to_datetime(df[date_col])
        df.set_index(date_col, inplace=True)
    return df


def fetch_data(symbol: str, asset_type: str = "auto", days: int = 90) -> pd.DataFrame:
    symbol = symbol.upper().strip()
    symbol = YAHOO_MAP.get(symbol, symbol)

    coin_id  = CRYPTO_IDS.get(symbol)
    is_crypto = asset_type == "crypto" or (asset_type == "auto" and coin_id is not None)

    if is_crypto and coin_id:
        try:
            return fetch_crypto(coin_id, days=days)
        except Exception:
            pass

    # Yahoo Finance query API dene
    for sym in [symbol, symbol + "=X", symbol + "-USD", symbol + ".IS"]:
        try:
            df = fetch_yf_api(sym, days=days)
            if not df.empty:
                return df
        except Exception:
            continue

    return pd.DataFrame()
