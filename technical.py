import pandas as pd
import pandas_ta as ta


def calculate(df: pd.DataFrame) -> dict:
    """Tüm teknik göstergeleri hesaplar, özet dict döner."""
    if df.empty or len(df) < 20:
        return {"hata": "Yeterli veri yok"}

    close = df["close"]
    high = df["high"]
    low = df["low"]
    volume = df["volume"]

    # Göstergeler
    df["rsi"] = ta.rsi(close, length=14)
    macd = ta.macd(close, fast=12, slow=26, signal=9)
    if macd is not None:
        df = pd.concat([df, macd], axis=1)
    bb = ta.bbands(close, length=20)
    if bb is not None:
        df = pd.concat([df, bb], axis=1)
    df["ema9"]   = ta.ema(close, length=9)
    df["ema21"]  = ta.ema(close, length=21)
    df["ema50"]  = ta.ema(close, length=50)
    df["sma200"] = ta.sma(close, length=200)

    last = df.iloc[-1]
    current_price = float(last["close"])

    # Destek / Direnç (son 30 günün min/max)
    recent = df.tail(30)
    support    = float(recent["low"].min())
    resistance = float(recent["high"].max())

    # RSI yorumu
    rsi_val = float(last.get("rsi", 50))
    if rsi_val > 70:
        rsi_yorum = "Aşırı alım bölgesi"
    elif rsi_val < 30:
        rsi_yorum = "Aşırı satım bölgesi"
    else:
        rsi_yorum = "Nötr"

    # MACD sütun adları pandas-ta formatında
    macd_col   = [c for c in df.columns if c.startswith("MACD_")]
    signal_col = [c for c in df.columns if c.startswith("MACDs_")]
    macd_val   = float(last[macd_col[0]])   if macd_col   else 0
    signal_val = float(last[signal_col[0]]) if signal_col else 0
    macd_yorum = "Yükseliş sinyali" if macd_val > signal_val else "Düşüş sinyali"

    # Bollinger
    bb_upper = [c for c in df.columns if c.startswith("BBU_")]
    bb_lower = [c for c in df.columns if c.startswith("BBL_")]
    bb_upper_val = float(last[bb_upper[0]]) if bb_upper else None
    bb_lower_val = float(last[bb_lower[0]]) if bb_lower else None

    # Trend (EMA9 > EMA21 > EMA50)
    ema9  = float(last.get("ema9",  0) or 0)
    ema21 = float(last.get("ema21", 0) or 0)
    ema50 = float(last.get("ema50", 0) or 0)
    if ema9 > ema21 > ema50:
        trend = "Güçlü Yükseliş Trendi"
    elif ema9 < ema21 < ema50:
        trend = "Güçlü Düşüş Trendi"
    else:
        trend = "Yatay / Karışık"

    # Hacim değişimi
    avg_vol = float(volume.tail(20).mean())
    last_vol = float(volume.iloc[-1])
    hacim_yorum = "Ortalamanın üzerinde" if last_vol > avg_vol else "Ortalamanın altında"

    return {
        "fiyat": current_price,
        "rsi": round(rsi_val, 2),
        "rsi_yorum": rsi_yorum,
        "macd": round(macd_val, 4),
        "macd_sinyal": round(signal_val, 4),
        "macd_yorum": macd_yorum,
        "bb_ust": round(bb_upper_val, 4) if bb_upper_val else None,
        "bb_alt": round(bb_lower_val, 4) if bb_lower_val else None,
        "ema9": round(ema9, 4),
        "ema21": round(ema21, 4),
        "ema50": round(ema50, 4),
        "destek": round(support, 4),
        "direnc": round(resistance, 4),
        "trend": trend,
        "hacim_yorum": hacim_yorum,
        "df": df,  # grafik için
    }
