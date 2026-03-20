import httpx

TIMEOUT = httpx.Timeout(600.0)


def get_models(base_url: str) -> list[str]:
    try:
        r = httpx.get(f"{base_url}/v1/models", timeout=5)
        r.raise_for_status()
        return [m["id"] for m in r.json().get("data", [])]
    except Exception:
        return []


async def analyze(symbol: str, indicators: dict, base_url: str, model: str) -> str:
    system_prompt = (
        "Sen deneyimli bir Türk finans analistisin. "
        "Yanıtlarını YALNIZCA Türkçe yaz, kesinlikle başka dil kullanma. "
        "Teknik analiz verilerini yorumlayarak net, anlaşılır Türkçe AL / SAT / BEKLE tavsiyesi ver. "
        "Yanıtın madde madde, kısa ve öz olsun. Sonuna sorumluluk reddi ekle."
    )

    user_prompt = f"""
{symbol} için teknik analiz verileri:

- Güncel Fiyat: {indicators.get('fiyat')}
- RSI: {indicators.get('rsi')} → {indicators.get('rsi_yorum')}
- MACD: {indicators.get('macd')} | Sinyal: {indicators.get('macd_sinyal')} → {indicators.get('macd_yorum')}
- Bollinger Üst: {indicators.get('bb_ust')} | Alt: {indicators.get('bb_alt')}
- Trend: {indicators.get('trend')}
- Destek: {indicators.get('destek')} | Direnç: {indicators.get('direnc')}
- Hacim: {indicators.get('hacim_yorum')}

Bu verilere göre detaylı Türkçe analiz yap ve AL / SAT / BEKLE tavsiyeni açıkla. Yanıtını Türkçe yaz.
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
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            r = await client.post(f"{base_url}/v1/chat/completions", json=payload)
            r.raise_for_status()
            return r.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"LMStudio bağlantı hatası: {e}"
