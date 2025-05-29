#!/usr/bin/env python3
"""
Analyse EMA/RSI + filtre actu (optionnel) et envoie les signaux Telegram.
Aucune exécution d'ordre. Conçu pour GitHub Actions (public repo).
"""
import os, requests, ccxt, pandas as pd, pandas_ta as ta
from datetime import datetime, timezone

TOKEN   = os.environ['TG_TOKEN']
CHAT_ID = os.environ['TG_CHAT_ID']
PAIR    = os.getenv('PAIR', 'BTC/USDT')
TF      = os.getenv('TF', '15m')
CP_KEY  = os.getenv('CP_KEY', '')

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

def main():
    ex = ccxt.binance()
    candles = ex.fetch_ohlcv(PAIR, TF, limit=100)
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
        msg = f"<b>{side} {PAIR}</b>\nPrix : <code>{price:.2f}</code>\nRSI : {rsi:.1f}\n{now} UTC"
        tg_send(msg)

if __name__ == '__main__':
    main()
