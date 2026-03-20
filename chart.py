import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd


def create_chart(df: pd.DataFrame, symbol: str) -> str:
    """Fiyat + RSI + MACD içeren interaktif Plotly grafiği üretir. HTML string döner."""
    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        row_heights=[0.6, 0.2, 0.2],
        vertical_spacing=0.03,
        subplot_titles=(f"{symbol} Fiyat", "RSI", "MACD"),
    )

    # Mum grafiği
    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df["open"], high=df["high"],
        low=df["low"],   close=df["close"],
        name="Fiyat",
        increasing_line_color="#26a69a",
        decreasing_line_color="#ef5350",
    ), row=1, col=1)

    # EMA'lar
    for col, color, name in [("ema9", "#f39c12", "EMA9"), ("ema21", "#3498db", "EMA21"), ("ema50", "#9b59b6", "EMA50")]:
        if col in df.columns:
            fig.add_trace(go.Scatter(x=df.index, y=df[col], line=dict(color=color, width=1), name=name), row=1, col=1)

    # Bollinger Bands
    if "bb_upper" in df.columns and "bb_lower" in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df["bb_upper"], line=dict(color="gray", width=1, dash="dot"), name="BB Üst"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df["bb_lower"], line=dict(color="gray", width=1, dash="dot"), name="BB Alt", fill="tonexty", fillcolor="rgba(128,128,128,0.1)"), row=1, col=1)

    # RSI
    if "rsi" in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df["rsi"], line=dict(color="#e67e22", width=1.5), name="RSI"), row=2, col=1)
        fig.add_hline(y=70, line_dash="dash", line_color="red",   row=2, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)

    # MACD
    if "macd" in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df["macd"],        line=dict(color="#3498db", width=1.5), name="MACD"),   row=3, col=1)
    if "macd_signal" in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df["macd_signal"], line=dict(color="#e74c3c", width=1.5), name="Sinyal"), row=3, col=1)
    if "macd_hist" in df.columns:
        colors = ["#26a69a" if v >= 0 else "#ef5350" for v in df["macd_hist"].fillna(0)]
        fig.add_trace(go.Bar(x=df.index, y=df["macd_hist"], marker_color=colors, name="Histogram"), row=3, col=1)

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#1a1a2e",
        plot_bgcolor="#16213e",
        font=dict(color="#eee", size=11),
        xaxis_rangeslider_visible=False,
        legend=dict(orientation="h", y=1.02, x=0),
        margin=dict(l=10, r=10, t=40, b=10),
        height=600,
    )

    return fig.to_html(full_html=False, include_plotlyjs="cdn", config={"responsive": True})
