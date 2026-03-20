from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request
import data_fetcher, technical, chart, llm, history
import os

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
    # Veri çek
    if file and file.filename:
        content = await file.read()
        df = data_fetcher.fetch_from_csv(content)
    else:
        df = data_fetcher.fetch_data(symbol)

    if df.empty:
        return JSONResponse({"hata": f"'{symbol}' için veri alınamadı. CSV yükleyebilirsiniz."}, status_code=400)

    # Teknik analiz
    indicators = technical.calculate(df)
    if "hata" in indicators:
        return JSONResponse({"hata": indicators["hata"]}, status_code=400)

    df_with_indicators = indicators.pop("df")

    # Grafik
    chart_html = chart.create_chart(df_with_indicators, symbol)

    # LLM yorumu
    yorum = llm.analyze(symbol, indicators, base_url, model)

    # Geçmişe kaydet
    history.save(symbol, indicators, yorum)

    return JSONResponse({
        "symbol": symbol,
        "indicators": indicators,
        "chart": chart_html,
        "yorum": yorum,
    })


@app.get("/history")
async def get_history(symbol: str = None):
    return {"history": history.get_recent(symbol)}
