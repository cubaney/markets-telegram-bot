import requests, pandas as pd, numpy as np, yfinance as yf
from datetime import datetime
import pytz

# === CONFIG ===
BOT_TOKEN = "7687498063:AAGfyTWpjoc-TfZPnO28DpA9d90ErxF_9e8"
CHAT_ID = "771393283"
TZ = pytz.timezone("Europe/Rome")

# Assets da monitorare
ASSETS = {
    "BTC": "BTC-USD",
    "ETH": "ETH-USD",
    "SOL": "SOL-USD",
    "S&P500": "^GSPC",
    "NASDAQ": "^NDX",
    "DAX": "^GDAXI",
    "FTSE MIB": "FTSEMIB.MI",
    "Gold": "GC=F",
    "Oil WTI": "CL=F",
    "EURUSD": "EURUSD=X"
}

def rsi(series, period=14):
    delta = series.diff()
    up = delta.clip(lower=0)
    down = -1 * delta.clip(upper=0)
    ma_up = up.ewm(com=(period - 1), min_periods=period).mean()
    ma_down = down.ewm(com=(period - 1), min_periods=period).mean()
    rs = ma_up / ma_down
    return 100 - (100 / (1 + rs))

def signal(rsi_val, price, ema20, ema50):
    if rsi_val < 35:
        return "🟢 BUY (forte)", "RSI molto basso — possibile rimbalzo"
    elif rsi_val < 40:
        return "🟢 BUY", "RSI in zona accumulo"
    elif rsi_val > 70 or (price > ema20 * 1.05):
        return "🔴 SELL / Take-Profit", "Prezzo esteso o RSI alto"
    else:
        return "🟡 WAIT", "Nessun segnale forte"

def analyze_asset(name, ticker):
    df = yf.download(ticker, period="90d", interval="1d", progress=False)
    close = df["Close"]
    ema20 = close.ewm(span=20).mean().iloc[-1]
    ema50 = close.ewm(span=50).mean().iloc[-1]
    rsi_val = rsi(close).iloc[-1]
    price = close.iloc[-1]
    sig, note = signal(rsi_val, price, ema20, ema50)
    return f"{name}: {price:.2f} | RSI {rsi_val:.1f} | EMA20 {ema20:.2f} | EMA50 {ema50:.2f}\n→ {sig} — {note}"

def main():
    now = datetime.now(TZ).strftime("%d/%m/%Y %H:%M")
    msg = f"📊 Analisi mercati — {now}\n\n"
    for name, ticker in ASSETS.items():
        try:
            msg += analyze_asset(name, ticker) + "\n\n"
        except Exception as e:
            msg += f"{name}: errore dati ({e})\n\n"
    send_telegram(msg)

def send_telegram(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"})

if __name__ == "__main__":
    main()
