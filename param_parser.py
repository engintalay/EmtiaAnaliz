"""Kullanıcı mesajından ve form'dan analiz parametrelerini çıkarır."""
import re
from technical import DEFAULTS


def parse_params(text: str, form_params: dict = None) -> dict:
    """
    Önce form_params'ı al, sonra serbest metinden override et.
    Örnek: "RSI 21 olsun, 180 günlük analiz yap, EMA 9 21 100"
    """
    p = {**DEFAULTS, **(form_params or {})}
    text_up = text.upper()

    # RSI periyodu: "RSI 21", "RSI periyodu 21", "RSI(21)"
    m = re.search(r'RSI[\s(]*(\d+)', text_up)
    if m:
        p["rsi_period"] = int(m.group(1))

    # MACD: "MACD 12 26 9"
    m = re.search(r'MACD[\s(]*(\d+)[,\s]+(\d+)[,\s]+(\d+)', text_up)
    if m:
        p["macd_fast"], p["macd_slow"], p["macd_signal"] = int(m.group(1)), int(m.group(2)), int(m.group(3))

    # Bollinger: "BB 20", "BOLLINGER 20"
    m = re.search(r'(?:BB|BOLLINGER)[\s(]*(\d+)', text_up)
    if m:
        p["bb_period"] = int(m.group(1))

    # Gün sayısı: "180 gün", "90 günlük", "son 365 gün"
    m = re.search(r'(\d+)\s*GÜN', text_up)
    if m:
        p["days"] = int(m.group(1))

    # Ay: "1 ay", "3 aylık", "son 6 ay"
    m = re.search(r'(\d+)\s*AY', text_up)
    if m:
        p["days"] = int(m.group(1)) * 30

    # Yıl: "1 yıl", "2 yıllık"
    m = re.search(r'(\d+)\s*YIL', text_up)
    if m:
        p["days"] = int(m.group(1)) * 365

    # EMA periyotları: "EMA 9 21 50 200"
    m = re.search(r'EMA[\s(]*([\d\s,]+)', text_up)
    if m:
        periods = [int(x) for x in re.findall(r'\d+', m.group(1))]
        if periods:
            p["ema_periods"] = periods

    return p


def params_summary(p: dict) -> str:
    """Kullanıcıya gösterilecek parametre özeti."""
    ema_str = ", ".join(str(x) for x in p.get("ema_periods", []))
    return (
        f"📐 **Analiz Parametreleri**\n"
        f"• RSI: {p.get('rsi_period')} periyot\n"
        f"• MACD: {p.get('macd_fast')}/{p.get('macd_slow')}/{p.get('macd_signal')}\n"
        f"• Bollinger: {p.get('bb_period')} periyot\n"
        f"• EMA: {ema_str}\n"
        f"• Veri: son {p.get('days')} gün"
    )
