import yfinance as yf
import requests
import pandas as pd
import io

COINGECKO_BASE = "https://api.coingecko.com/api/v3"


def fetch_crypto(symbol: str, days: int = 90) -> pd.DataFrame:
    """CoinGecko'dan kripto verisi çeker."""
    # Sembolü coin id'ye çevir
    coin_id = symbol.lower().replace("usdt", "").replace("usd", "").strip()
    url = f"{COINGECKO_BASE}/coins/{coin_id}/market_chart"
    params = {"vs_currency": "usd", "days": days, "interval": "daily"}
    r = requests.get(url, params=params, timeout=10)
    r.raise_for_status()
    data = r.json()
    prices = data["prices"]
    volumes = {v[0]: v[1] for v in data["total_volumes"]}
    df = pd.DataFrame(prices, columns=["timestamp", "close"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    df.set_index("timestamp", inplace=True)
    df["volume"] = df.index.map(lambda t: volumes.get(int(t.timestamp() * 1000), 0))
    df["open"] = df["close"].shift(1).fillna(df["close"])
    df["high"] = df["close"] * 1.01
    df["low"] = df["close"] * 0.99
    return df


def fetch_yfinance(symbol: str, period: str = "3mo") -> pd.DataFrame:
    """yfinance'den hisse/emtia verisi çeker."""
    ticker = yf.Ticker(symbol)
    df = ticker.history(period=period)
    df.index = pd.to_datetime(df.index)
    df.columns = [c.lower() for c in df.columns]
    return df[["open", "high", "low", "close", "volume"]]


def fetch_from_csv(content: bytes) -> pd.DataFrame:
    """Kullanıcının yüklediği CSV'den veri okur."""
    df = pd.read_csv(io.BytesIO(content))
    df.columns = [c.lower().strip() for c in df.columns]
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"])
        df.set_index("date", inplace=True)
    return df


def fetch_data(symbol: str, asset_type: str = "auto") -> pd.DataFrame:
    """
    asset_type: 'crypto', 'stock', 'auto'
    Önce internet, hata alırsa boş DataFrame döner (CSV fallback için).
    """
    symbol = symbol.upper().strip()

    # Kripto tespiti
    crypto_keywords = ["BTC", "ETH", "BNB", "SOL", "XRP", "DOGE", "ADA", "AVAX", "DOT", "MATIC"]
    is_crypto = asset_type == "crypto" or (asset_type == "auto" and symbol in crypto_keywords)

    try:
        if is_crypto:
            coin_id = symbol.lower()
            return fetch_crypto(coin_id)
        else:
            return fetch_yfinance(symbol)
    except Exception:
        # yfinance fallback for crypto too
        try:
            return fetch_yfinance(symbol + "-USD")
        except Exception:
            return pd.DataFrame()
