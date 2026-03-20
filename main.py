from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request
import data_fetcher, technical, chart, llm, history, param_parser
from logger import log
import re, os, json, asyncio

def extract_symbol(text: str) -> str:
    text = text.strip().upper()
    for sym in data_fetcher.CRYPTO_IDS:
        if re.search(rf'\b{sym}\b', text):
            return sym
    for sym in data_fetcher.YAHOO_MAP:
        if re.search(rf'\b{sym}\b', text):
            return sym
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


@app.get("/defaults")
async def get_defaults():
    return technical.DEFAULTS


@app.post("/analyze")
async def analyze(
    request: Request,
    symbol: str = Form(...),
    base_url: str = Form("http://localhost:1234"),
    model: str = Form(...),
    form_params: str = Form("{}"),   # JSON string
    file: UploadFile = File(None),
):
    raw_input = symbol
    symbol = extract_symbol(symbol)
    client_ip = request.client.host if request.client else "bilinmiyor"

    # Parametreleri çöz: form + serbest metin
    try:
        fp = json.loads(form_params)
    except Exception:
        fp = {}
    params = param_parser.parse_params(raw_input, fp)

    log.info(f"İSTEK | ip={client_ip} | girdi='{raw_input}' → sembol='{symbol}' | model={model} | params={params}")

    try:
        if file and file.filename:
            content = await file.read()
            df = await asyncio.to_thread(data_fetcher.fetch_from_csv, content)
            log.info(f"VERİ  | CSV: {file.filename}, {len(df)} satır")
        else:
            df = await asyncio.to_thread(data_fetcher.fetch_data, symbol, "auto", params.get("days", 90))
            log.info(f"VERİ  | {symbol} → {len(df)} satır")

        if df.empty:
            log.warning(f"HATA  | {symbol} veri alınamadı")
            return JSONResponse({"hata": f"'{symbol}' için veri alınamadı."}, status_code=400)

        indicators = technical.calculate(df, params)
        if "hata" in indicators:
            log.warning(f"HATA  | Teknik: {indicators['hata']}")
            return JSONResponse({"hata": indicators["hata"]}, status_code=400)

        log.info(f"ANALİZ| {symbol} | fiyat={indicators.get('fiyat')} RSI={indicators.get('rsi')} trend={indicators.get('trend')}")

        df_ind = indicators.pop("df")
        used_params = indicators.pop("params")
        chart_html = chart.create_chart(df_ind, symbol, used_params)
        param_info = param_parser.params_summary(used_params)

        yorum = await llm.analyze(symbol, indicators, base_url, model)
        log.info(f"LLM   | {symbol} | {len(yorum)} karakter")

        history.save(symbol, indicators, yorum)

        return JSONResponse({
            "symbol":      symbol,
            "indicators":  indicators,
            "chart":       chart_html,
            "yorum":       yorum,
            "param_info":  param_info,
            "params":      used_params,
        })

    except Exception as e:
        log.error(f"KRİTİK| {symbol} | {type(e).__name__}: {e}", exc_info=True)
        return JSONResponse({"hata": f"Beklenmeyen hata: {e}"}, status_code=500)


@app.get("/history")
async def get_history(symbol: str = None):
    return {"history": history.get_recent(symbol)}
