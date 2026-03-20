import logging
import os
from datetime import datetime

os.makedirs("logs", exist_ok=True)

def get_logger(name: str = "emtia") -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger  # zaten kurulu

    logger.setLevel(logging.DEBUG)

    # Günlük dosya: logs/2026-03-20.log
    today = datetime.now().strftime("%Y-%m-%d")
    fh = logging.FileHandler(f"logs/{today}.log", encoding="utf-8")
    fh.setLevel(logging.DEBUG)

    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)

    fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S")
    fh.setFormatter(fmt)
    ch.setFormatter(fmt)

    logger.addHandler(fh)
    logger.addHandler(ch)
    return logger

log = get_logger()
