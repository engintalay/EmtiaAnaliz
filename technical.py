import pandas as pd
import ta

# Varsayılan parametreler
DEFAULTS = {
    "rsi_period": 14,
    "macd_fast": 12,
    "macd_slow": 26,
    "macd_signal": 9,
    "bb_period": 20,
    "ema_periods": [9, 21, 50],
    "days": 90,
}


def calculate(df: pd.DataFrame, params: dict = None) -> dict:
    p = {**DEFAULTS, **(params or {})}

    if df.empty or len(df) < 20:
        return {"hata": "Yeterli veri yok"}

    close  = df["close"]
    high   = df["high"]
    low    = df["low"]
    volume = df["volume"]

    # RSI
    df["rsi"] = ta.momentum.RSIIndicator(close, window=p["rsi_period"]).rsi()

    # MACD
    macd_ind = ta.trend.MACD(close, window_fast=p["macd_fast"], window_slow=p["macd_slow"], window_sign=p["macd_signal"])
    df["macd"]        = macd_ind.macd()
    df["macd_signal"] = macd_ind.macd_signal()
    df["macd_hist"]   = macd_ind.macd_diff()

    # Bollinger
    bb = ta.volatility.BollingerBands(close, window=p["bb_period"])
    df["bb_upper"] = bb.bollinger_hband()
    df["bb_lower"] = bb.bollinger_lband()

    # EMA'lar
    for period in p["ema_periods"]:
        df[f"ema{period}"] = ta.trend.EMAIndicator(close, window=period).ema_indicator()

    last = df.iloc[-1]
    current_price = float(last["close"])

    recent     = df.tail(30)
    support    = float(recent["low"].min())
    resistance = float(recent["high"].max())

    rsi_val   = float(last["rsi"]) if pd.notna(last["rsi"]) else 50
    rsi_yorum = "Aşırı alım bölgesi" if rsi_val > 70 else ("Aşırı satım bölgesi" if rsi_val < 30 else "Nötr")

    macd_val   = float(last["macd"])        if pd.notna(last["macd"])        else 0
    signal_val = float(last["macd_signal"]) if pd.notna(last["macd_signal"]) else 0
    macd_yorum = "Yükseliş sinyali" if macd_val > signal_val else "Düşüş sinyali"

    ema_vals = {}
    for period in p["ema_periods"]:
        v = last.get(f"ema{period}")
        ema_vals[f"ema{period}"] = round(float(v), 4) if v is not None and pd.notna(v) else 0

    # Trend: ilk 3 EMA'ya göre
    ema_list = [ema_vals.get(f"ema{p_}", 0) for p_ in p["ema_periods"][:3]]
    if len(ema_list) >= 2 and all(ema_list[i] > ema_list[i+1] for i in range(len(ema_list)-1)):
        trend = "Güçlü Yükseliş Trendi"
    elif len(ema_list) >= 2 and all(ema_list[i] < ema_list[i+1] for i in range(len(ema_list)-1)):
        trend = "Güçlü Düşüş Trendi"
    else:
        trend = "Yatay / Karışık"

    avg_vol     = float(volume.tail(20).mean())
    last_vol    = float(volume.iloc[-1])
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
        **ema_vals,
        "destek":      round(support, 4),
        "direnc":      round(resistance, 4),
        "trend":       trend,
        "hacim_yorum": hacim_yorum,
        "params":      p,
        "df":          df,
    }
