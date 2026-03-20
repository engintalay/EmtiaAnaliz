from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request
import data_fetcher, technical, chart, llm, history
from logger import log
import re, os

# Mesajdan sembol çıkar: "BTC analiz et" → "BTC"
def extract_symbol(text: str) -> str:
    text = text.strip().upper()
    # Bilinen kripto listesi
    for sym in data_fetcher.CRYPTO_IDS:
        if re.search(rf'\b{sym}\b', text):
            return sym
    # Bilinen takma adlar
    for sym in data_fetcher.YAHOO_MAP:
        if re.search(rf'\b{sym}\b', text):
            return sym
    # İlk kelime büyük harf ve kısa ise sembol say (AAPL, THYAO vb.)
    first = text.split()[0]
    if re.match(r'^[A-Z0-9.=^]{1,10}$', first):
        return first
    return text

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/models")
async def get_models(base_url: str = "http://localhost:1234"):
    return {"models": llm.get_models(base_url)}


@app.post("/analyze")
async def analyze(
    symbol: str = Form(...),
    base_url: str = Form("http://localhost:1234"),
    model: str = Form(...),
    file: UploadFile = File(None),
):
    raw_input = symbol
    symbol = extract_symbol(symbol)
    log.info(f"İSTEK | girdi='{raw_input}' → sembol='{symbol}' | model={model} | url={base_url}")

    try:
        # Veri çek
        if file and file.filename:
            content = await file.read()
            df = data_fetcher.fetch_from_csv(content)
            log.info(f"VERİ  | CSV yüklendi: {file.filename}, {len(df)} satır")
        else:
            df = data_fetcher.fetch_data(symbol)
            log.info(f"VERİ  | {symbol} → {len(df)} satır")

        if df.empty:
            log.warning(f"HATA  | {symbol} için veri alınamadı")
            return JSONResponse({"hata": f"'{symbol}' için veri alınamadı. CSV yükleyebilirsiniz."}, status_code=400)

        # Teknik analiz
        indicators = technical.calculate(df)
        if "hata" in indicators:
            log.warning(f"HATA  | Teknik analiz: {indicators['hata']}")
            return JSONResponse({"hata": indicators["hata"]}, status_code=400)

        log.info(f"ANALİZ| {symbol} | fiyat={indicators.get('fiyat')} RSI={indicators.get('rsi')} trend={indicators.get('trend')}")

        df_with_indicators = indicators.pop("df")
        chart_html = chart.create_chart(df_with_indicators, symbol)

        # LLM yorumu
        yorum = llm.analyze(symbol, indicators, base_url, model)
        log.info(f"LLM   | {symbol} | yorum uzunluğu={len(yorum)} karakter")

        history.save(symbol, indicators, yorum)

        return JSONResponse({
            "symbol": symbol,
            "indicators": indicators,
            "chart": chart_html,
            "yorum": yorum,
        })

    except Exception as e:
        log.error(f"KRİTİK| {symbol} | {type(e).__name__}: {e}", exc_info=True)
        return JSONResponse({"hata": f"Beklenmeyen hata: {e}"}, status_code=500)


@app.get("/history")
async def get_history(symbol: str = None):
    return {"history": history.get_recent(symbol)}
