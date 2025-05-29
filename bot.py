import os
import time
import ccxt
import pandas as pd
import pandas_ta as ta
import requests
from datetime import datetime, timezone

TOKEN   = os.environ['TG_TOKEN']
CHAT_ID = os.environ['TG_CHAT_ID']
CP_KEY  = os.getenv('CP_KEY', '')

PAIRS = ['BTC/USD', 'ETH/USD', 'ADA/USD', 'SHIB/USD', 'XRP/USD', 'DOGE/USD']
TF = '15m'

def tg_send(text: str):
    url = f'https://api.telegram.org/bot{TOKEN}/sendMessage'
    requests.post(url, json={'chat_id': CHAT_ID, 'text': text, 'parse_mode': 'HTML'}, timeout=10)

def get_sentiment() -> float:
    if not CP_KEY:
        return 0.0
    try:
        url = 'https://cryptopanic.com/api/v1/posts/'
        r = requests.get(url, params={'auth_token': CP_KEY, 'public': 'true'}, timeout=10).json()
        news = r.get('results', [])[:50]
        return sum(1 if n.get('positive') else -1 for n in news) / len(news) if news else 0.0
    except:
        return 0.0

def analyze_pair(pair):
    ex = ccxt.kraken()
    try:
        candles = ex.fetch_ohlcv(pair, TF, limit=100)
    except Exception as e:
        print(f"Erreur lors de la récupération des données pour {pair}: {e}")
        return
    df = pd.DataFrame(candles, columns=['ts', 'o', 'h', 'l', 'c', 'v'])
    df['dt'] = pd.to_datetime(df['ts'], unit='ms')
    df.set_index('dt', inplace=True)

    df['ema20'] = ta.ema(df['c'], length=20)
    df['ema50'] = ta.ema(df['c'], length=50)
    df['rsi14'] = ta.rsi(df['c'], length=14)

    sent = get_sentiment()
    bull = df['ema20'].iloc[-1] > df['ema50'].iloc[-1]
    rsi = df['rsi14'].iloc[-1]
    price = df['c'].iloc[-1]
    now = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M')

    side = None
    if bull and rsi < 30 and sent > -0.2:
        side = 'BUY'
    elif not bull and rsi > 70 and sent < 0.2:
        side = 'SELL'

    if side:
        msg = f"<b>{side} {pair}</b>\nPrix : <code>{price:.2f}</code>\nRSI : {rsi:.1f}\n{now} UTC"
        tg_send(msg)

def main():
    for pair in PAIRS:
        analyze_pair(pair)
        time.sleep(1.2)  # Pour éviter le rate limit de Telegram

if __name__ == '__main__':
    main()
