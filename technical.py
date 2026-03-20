import pandas as pd
import ta


def calculate(df: pd.DataFrame) -> dict:
    if df.empty or len(df) < 20:
        return {"hata": "Yeterli veri yok"}

    close  = df["close"]
    high   = df["high"]
    low    = df["low"]
    volume = df["volume"]

    # RSI
    df["rsi"] = ta.momentum.RSIIndicator(close, window=14).rsi()

    # MACD
    macd_ind = ta.trend.MACD(close, window_fast=12, window_slow=26, window_sign=9)
    df["macd"]        = macd_ind.macd()
    df["macd_signal"] = macd_ind.macd_signal()
    df["macd_hist"]   = macd_ind.macd_diff()

    # Bollinger
    bb = ta.volatility.BollingerBands(close, window=20)
    df["bb_upper"] = bb.bollinger_hband()
    df["bb_lower"] = bb.bollinger_lband()

    # EMA / SMA
    df["ema9"]   = ta.trend.EMAIndicator(close, window=9).ema_indicator()
    df["ema21"]  = ta.trend.EMAIndicator(close, window=21).ema_indicator()
    df["ema50"]  = ta.trend.EMAIndicator(close, window=50).ema_indicator()
    df["sma200"] = ta.trend.SMAIndicator(close, window=200).sma_indicator()

    last = df.iloc[-1]
    current_price = float(last["close"])

    # Destek / Direnç
    recent     = df.tail(30)
    support    = float(recent["low"].min())
    resistance = float(recent["high"].max())

    # RSI yorumu
    rsi_val = float(last["rsi"]) if pd.notna(last["rsi"]) else 50
    rsi_yorum = "Aşırı alım bölgesi" if rsi_val > 70 else ("Aşırı satım bölgesi" if rsi_val < 30 else "Nötr")

    # MACD yorumu
    macd_val   = float(last["macd"])        if pd.notna(last["macd"])        else 0
    signal_val = float(last["macd_signal"]) if pd.notna(last["macd_signal"]) else 0
    macd_yorum = "Yükseliş sinyali" if macd_val > signal_val else "Düşüş sinyali"

    # Trend
    ema9  = float(last["ema9"])  if pd.notna(last["ema9"])  else 0
    ema21 = float(last["ema21"]) if pd.notna(last["ema21"]) else 0
    ema50 = float(last["ema50"]) if pd.notna(last["ema50"]) else 0
    if ema9 > ema21 > ema50:
        trend = "Güçlü Yükseliş Trendi"
    elif ema9 < ema21 < ema50:
        trend = "Güçlü Düşüş Trendi"
    else:
        trend = "Yatay / Karışık"

    # Hacim
    avg_vol  = float(volume.tail(20).mean())
    last_vol = float(volume.iloc[-1])
    hacim_yorum = "Ortalamanın üzerinde" if last_vol > avg_vol else "Ortalamanın altında"

    return {
        "fiyat":       current_price,
        "rsi":         round(rsi_val, 2),
        "rsi_yorum":   rsi_yorum,
        "macd":        round(macd_val, 4),
        "macd_sinyal": round(signal_val, 4),
        "macd_yorum":  macd_yorum,
        "bb_ust":      round(float(last["bb_upper"]), 4) if pd.notna(last["bb_upper"]) else None,
        "bb_alt":      round(float(last["bb_lower"]), 4) if pd.notna(last["bb_lower"]) else None,
        "ema9":        round(ema9, 4),
        "ema21":       round(ema21, 4),
        "ema50":       round(ema50, 4),
        "destek":      round(support, 4),
        "direnc":      round(resistance, 4),
        "trend":       trend,
        "hacim_yorum": hacim_yorum,
        "df":          df,
    }
