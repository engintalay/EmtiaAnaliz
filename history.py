import json
import os
from datetime import datetime

HISTORY_FILE = "data/history.json"


def _load() -> list:
    if not os.path.exists(HISTORY_FILE):
        return []
    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save(symbol: str, indicators: dict, yorum: str):
    os.makedirs("data", exist_ok=True)
    history = _load()
    record = {
        "tarih": datetime.now().isoformat(),
        "sembol": symbol,
        "fiyat": indicators.get("fiyat"),
        "rsi": indicators.get("rsi"),
        "trend": indicators.get("trend"),
        "yorum_ozet": yorum[:300],
    }
    history.append(record)
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


def get_recent(symbol: str = None, limit: int = 5) -> list:
    history = _load()
    if symbol:
        history = [h for h in history if h["sembol"].upper() == symbol.upper()]
    return history[-limit:]
