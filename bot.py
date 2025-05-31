import os
import time
import ccxt
import pandas as pd
import pandas_ta as ta
import requests
from telegram import Bot
from telegram.ext import Updater, CommandHandler
from datetime import datetime, timezone

TOKEN   = os.environ['TG_TOKEN']
CHAT_ID = os.environ['TG_CHAT_ID']
CP_KEY  = os.getenv('CP_KEY', '')

PAIRS = ['BTC/USD', 'ETH/USD', 'ADA/USD', 'SHIB/USD', 'XRP/USD', 'DOGE/USD']
TF = '1h'

def tg_send(text: str):
    bot = Bot(token=TOKEN)
    try:
        bot.send_message(chat_id=CHAT_ID, text=text, parse_mode="HTML")
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
        return

    if side:
        tg_msg = (
            f"<b>{side} {pair}</b>\n"
            f"Prix : <code>{price:.5f}</code>\n"
            f"RSI : {rsi:.1f}\n"
            f"{now} UTC"
        )
        tg_send(tg_msg)

# 🔁 Analyse manuelle depuis Telegram avec /analyse BTC/USD
def handle_analyse(update, context):
    try:
        pair = ' '.join(context.args).upper()
        if not pair:
            update.message.reply_text("❗️ Utilisation : /analyse BTC/USD")
            return

        ex = ccxt.kraken()
        candles = ex.fetch_ohlcv(pair, TF, limit=100)
        df = pd.DataFrame(candles, columns=['ts', 'o', 'h', 'l', 'c', 'v'])
        df['dt'] = pd.to_datetime(df['ts'], unit='ms')
        df.set_index('dt', inplace=True)

        df['ema20'] = ta.ema(df['c'], length=20)
        df['ema50'] = ta.ema(df['c'], length=50)
        df['rsi'] = ta.rsi(df['c'], length=14)

        rsi = df['rsi'].iloc[-1]
        ema20 = df['ema20'].iloc[-1]
        ema50 = df['ema50'].iloc[-1]
        price = df['c'].iloc[-1]
        now = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M')
        tendance = "Haussière" if ema20 > ema50 else "Baissière"

        message = (
            f"📊 Analyse {pair}\n"
            f"Prix : {price:.5f}\n"
            f"RSI : {rsi:.1f}\n"
            f"EMA20 : {ema20:.2f}\n"
            f"EMA50 : {ema50:.2f}\n"
            f"Tendance : {tendance}\n"
            f"{now} UTC"
        )
        update.message.reply_text(message, parse_mode="HTML")

    except Exception as e:
        update.message.reply_text(f"⚠️ Erreur : {e}")

# 💬 Activation du mode conversationnel Telegram
def start_bot_listener():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("analyse", handle_analyse))
    updater.start_polling()
    updater.idle()

# 🚀 Exécution principale
def main():
    for pair in PAIRS:
        print(f"🔍 Analyse de {pair}")
        analyze_pair(pair)
        time.sleep(1.2)

if __name__ == '__main__':
    main()
    start_bot_listener()
