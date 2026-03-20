import requests


def get_models(base_url: str) -> list[str]:
    """LMStudio'daki mevcut modelleri listeler."""
    try:
        r = requests.get(f"{base_url}/v1/models", timeout=5)
        r.raise_for_status()
        return [m["id"] for m in r.json().get("data", [])]
    except Exception:
        return []


def analyze(symbol: str, indicators: dict, base_url: str, model: str) -> str:
    """Teknik analiz verilerini LMStudio'ya gönderir, Türkçe yorum alır."""
    system_prompt = (
        "Sen deneyimli bir Türk finans analistisin. "
        "Kullanıcıya teknik analiz verilerini yorumlayarak net, anlaşılır Türkçe al/sat/bekle tavsiyesi veriyorsun. "
        "Yanıtın kısa, net ve madde madde olsun. Sorumluluk reddi ekle."
    )

    user_prompt = f"""
{symbol} için teknik analiz verileri:

- Güncel Fiyat: {indicators.get('fiyat')}
- RSI (14): {indicators.get('rsi')} → {indicators.get('rsi_yorum')}
- MACD: {indicators.get('macd')} | Sinyal: {indicators.get('macd_sinyal')} → {indicators.get('macd_yorum')}
- Bollinger Üst: {indicators.get('bb_ust')} | Alt: {indicators.get('bb_alt')}
- EMA9: {indicators.get('ema9')} | EMA21: {indicators.get('ema21')} | EMA50: {indicators.get('ema50')}
- Destek: {indicators.get('destek')} | Direnç: {indicators.get('direnc')}
- Trend: {indicators.get('trend')}
- Hacim: {indicators.get('hacim_yorum')}

Bu verilere göre detaylı analiz yap ve AL / SAT / BEKLE tavsiyeni açıkla.
"""

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_prompt},
        ],
        "temperature": 0.3,
        "max_tokens": 1024,
    }

    try:
        r = requests.post(f"{base_url}/v1/chat/completions", json=payload, timeout=180)
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"LMStudio bağlantı hatası: {e}"
