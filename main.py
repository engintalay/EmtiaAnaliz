from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request
import data_fetcher, technical, chart, llm, history, param_parser
from logger import log
import re, os, json, asyncio

last_symbol = {}  # {"symbol": "BTC"} — son kullanılan sembol

def extract_symbol(text: str) -> str:
    text_up = text.strip().upper()
    for sym in data_fetcher.CRYPTO_IDS:
        if re.search(rf'\b{sym}\b', text_up):
            return sym
    for sym in data_fetcher.YAHOO_MAP:
        if re.search(rf'\b{sym}\b', text_up):
            return sym
    first = text_up.split()[0]
    # Sadece harf içeren ve 2+ karakter olan kelimeleri sembol say
    if re.match(r'^[A-Z]{2,10}([.=^][A-Z0-9]+)?$', first):
        return first
    # Sembol bulunamadıysa son kullanılan sembolü döndür
    return last_symbol.get("symbol", text_up)

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
    form_params: str = Form("{}"),
    thinking: bool = Form(False),
    file: UploadFile = File(None),
):
    raw_input = symbol
    symbol = extract_symbol(symbol)
    client_ip = request.client.host if request.client else "bilinmiyor"

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

        df_ind      = indicators.pop("df")
        used_params = indicators.pop("params")
        chart_html  = chart.create_chart(df_ind, symbol, used_params)
        param_info  = param_parser.params_summary(used_params)
        last_symbol["symbol"] = symbol  # bir sonraki istek için hatırla

        # Grafik + göstergeler hemen dön — LLM stream ayrı endpoint'ten
        return JSONResponse({
            "symbol":     symbol,
            "indicators": indicators,
            "chart":      chart_html,
            "param_info": param_info,
            "params":     used_params,
        })

    except Exception as e:
        log.error(f"KRİTİK| {symbol} | {type(e).__name__}: {e}", exc_info=True)
        return JSONResponse({"hata": f"Beklenmeyen hata: {e}"}, status_code=500)


@app.post("/analyze/stream")
async def analyze_stream(
    request: Request,
    symbol: str = Form(...),
    base_url: str = Form("http://localhost:1234"),
    model: str = Form(...),
    indicators: str = Form(...),
    thinking: bool = Form(False),
):
    symbol    = extract_symbol(symbol)
    client_ip = request.client.host if request.client else "bilinmiyor"
    try:
        ind = json.loads(indicators)
    except Exception:
        ind = {}

    log.info(f"STREAM| ip={client_ip} | sembol='{symbol}' | thinking={thinking}")
    full_text = []

    async def event_gen():
        async for chunk in llm.analyze_stream(symbol, ind, base_url, model, thinking):
            if '"token"' in chunk:
                token = json.loads(chunk[5:])["token"]
                full_text.append(token)
            yield chunk
        history.save(symbol, ind, "".join(full_text))
        log.info(f"STREAM| {symbol} tamamlandı, {len(full_text)} token")

    return StreamingResponse(event_gen(), media_type="text/event-stream")


@app.get("/history")
async def get_history(symbol: str = None):
    return {"history": history.get_recent(symbol)}
