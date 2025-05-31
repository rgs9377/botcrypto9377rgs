import os
import time
import ccxt
import pandas as pd
import pandas_ta as ta
import requests
from telegram import Bot
from datetime import datetime,timezone


TOKEN   = os.environ['TG_TOKEN']
CHAT_ID = os.environ['TG_CHAT_ID']
CP_KEY  = os.getenv('CP_KEY', '')

PAIRS = ['BTC/USD', 'ETH/USD', 'ADA/USD', 'SHIB/USD', 'XRP/USD', 'DOGE/USD']
TF = '1h'


def tg_send(text: str):
    bot = Bot(token=os.environ['TG_TOKEN'])
    try:
        bot.send_message(chat_id=os.environ['TG_CHAT_ID'], text=text, parse_mode="HTML")
    except Exception as e:
        print(f"[Telegram Error] {e}")

def get_sentiment() -> float:
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
        side = '🟢 LONG'
    elif not bull and rsi > 70 and sent < 0.2:
        side = '🔴 SHORT'
    else:
        return  # aucun signal

    if side:
           tg_msg = (
        f"<b>{side} {pair}</b>\n"
        f"Prix : <code>{price:.5f}</code>\n"
        f"RSI : {rsi:.1f}\n"
        f"{now} UTC"
    )
        


def main():
    for pair in PAIRS:
        print(f"🔍 Analyse de {pair}")
        analyze_pair(pair)
        time.sleep(1.2)

if __name__ == '__main__':
    main()
