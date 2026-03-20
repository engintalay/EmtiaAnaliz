import httpx
from fastapi.responses import StreamingResponse
import json

TIMEOUT = httpx.Timeout(600.0)


def get_models(base_url: str) -> list[str]:
    try:
        r = httpx.get(f"{base_url}/v1/models", timeout=5)
        r.raise_for_status()
        return [m["id"] for m in r.json().get("data", [])]
    except Exception:
        return []


async def analyze(symbol: str, indicators: dict, base_url: str, model: str, thinking: bool = False) -> str:
    """Tek seferde yanıt — geçmiş kaydı için kullanılır."""
    system_prompt, user_prompt = _build_prompts(symbol, indicators)
    payload = _build_payload(model, system_prompt, user_prompt, thinking, stream=False)
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            r = await client.post(f"{base_url}/v1/chat/completions", json=payload)
            r.raise_for_status()
            return r.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"LMStudio bağlantı hatası: {e}"


async def analyze_stream(symbol: str, indicators: dict, base_url: str, model: str, thinking: bool = False):
    """SSE stream — token token yield eder."""
    system_prompt, user_prompt = _build_prompts(symbol, indicators)
    payload = _build_payload(model, system_prompt, user_prompt, thinking, stream=True)
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            async with client.stream("POST", f"{base_url}/v1/chat/completions", json=payload) as r:
                async for line in r.aiter_lines():
                    if not line.startswith("data:"):
                        continue
                    data = line[5:].strip()
                    if data == "[DONE]":
                        yield "data: [DONE]\n\n"
                        return
                    try:
                        chunk = json.loads(data)
                        token = chunk["choices"][0]["delta"].get("content", "")
                        if token:
                            yield f"data: {json.dumps({'token': token})}\n\n"
                    except Exception:
                        continue
    except Exception as e:
        yield f"data: {json.dumps({'error': str(e)})}\n\n"


def _build_prompts(symbol, indicators):
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
    return system_prompt, user_prompt


def _build_payload(model, system_prompt, user_prompt, thinking, stream):
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_prompt},
        ],
        "temperature": 0.3,
        "max_tokens": 1024,
        "stream": stream,
    }
    if not thinking:
        payload["thinking"] = {"type": "disabled"}
    return payload

