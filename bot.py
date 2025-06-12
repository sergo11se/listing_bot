import time
import requests
import logging
import json
import os
from flask import Flask
from threading import Thread

# Telegram настройки
TOKEN = '7683066723:AAHot2507_9RrkpNCMh5QKLi0cQr7cPEVH8'
CHAT_ID = '5305138065'

# Файлы для хранения отправленных сообщений
SENT_BINANCE_FILE = 'sent_binance.json'
SENT_UPBIT_FILE = 'sent_upbit.json'
SENT_COINBASE_FILE = 'sent_coinbase.json'

# Flask — для Render
app = Flask(__name__)

@app.route('/')
def index():
    return "Bot is running!"

# Telegram отправка сообщений
def send_telegram_message(message):
    url = f'https://api.telegram.org/bot{TOKEN}/sendMessage'
    payload = {'chat_id': CHAT_ID, 'text': message}
    try:
        requests.post(url, data=payload)
    except Exception as e:
        logging.warning(f'Не удалось отправить сообщение в Telegram: {e}')

def load_sent(filename):
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            return set(json.load(f))
    return set()

def save_sent(filename, sent_set):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(list(sent_set), f, ensure_ascii=False)

# Проверка Binance
def check_binance():
    sent = load_sent(SENT_BINANCE_FILE)
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        url = 'https://www.binance.com/bapi/composite/v1/public/cms/article/list/query?type=1&pageNo=1&pageSize=10'
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            logging.warning(f'Binance вернул статус: {response.status_code}')
            return

        # Выведем содержимое для отладки
        logging.info(f'Binance raw response: {response.text[:500]}')

        data = response.json()

        new_sent = set(sent)
        for article in data.get('data', {}).get('articles', []):
            title = article.get('title', '')
            if 'will list' in title.lower() and title not in sent:
                send_telegram_message(f'📢 Binance Listing: {title}')
                new_sent.add(title)

        save_sent(SENT_BINANCE_FILE, new_sent)
    except Exception as e:
        logging.warning(f'⚠️ Ошибка Binance: {e}')


        save_sent(SENT_BINANCE_FILE, new_sent)
    except Exception as e:
        logging.warning(f'⚠️ Ошибка Binance: {e}')

# Проверка Upbit
def check_upbit():
    sent = load_sent(SENT_UPBIT_FILE)
    try:
        url = 'https://api.upbit.com/v1/market/all'
        response = requests.get(url)
        data = response.json()

        # В Upbit листинг новой монеты можно распознать по новому market_code
        # Для примера — считаем новые market_code, которых не было ранее.
        new_sent = set(sent)
        for market in data:
            market_code = market.get('market', '')
            korean_name = market.get('korean_name', '')
            if market_code not in sent and market_code.startswith('KRW-'):  # фильтр по рынку (можно менять)
                send_telegram_message(f'📢 Upbit Listing: {market_code} - {korean_name}')
                new_sent.add(market_code)

        save_sent(SENT_UPBIT_FILE, new_sent)
    except Exception as e:
        logging.warning(f'⚠️ Ошибка Upbit: {e}')

# Проверка Coinbase
def check_coinbase():
    sent = load_sent(SENT_COINBASE_FILE)
    try:
        # Для примера возьмём официальный Coinbase API с list coins
        url = 'https://api.coinbase.com/v2/currencies'
        response = requests.get(url)
        data = response.json()

        new_sent = set(sent)
        for coin in data.get('data', []):
            coin_id = coin.get('id', '')
            coin_name = coin.get('name', '')
            if coin_id not in sent:
                # Отправим уведомление о новой валюте на Coinbase (пример)
                send_telegram_message(f'📢 Coinbase Currency: {coin_name} ({coin_id})')
                new_sent.add(coin_id)

        save_sent(SENT_COINBASE_FILE, new_sent)
    except Exception as e:
        logging.warning(f'⚠️ Ошибка Coinbase: {e}')

# Основной цикл
def run_bot():
    last_notify = 0
    while True:
        logging.info("📡 Проверка Binance...")
        check_binance()
        logging.info("📡 Проверка Upbit...")
        check_upbit()
        logging.info("📡 Проверка Coinbase...")
        check_coinbase()

        # Уведомление о работе каждый час
        if time.time() - last_notify >= 3600:
            send_telegram_message("✅ Бот работает. Всё в порядке.")
            last_notify = time.time()

        time.sleep(300)  # Проверка каждые 5 минут

# Запуск Flask + бота
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    Thread(target=run_bot).start()
    app.run(host='0.0.0.0', port=10000)
