import time
import requests
import logging
from bs4 import BeautifulSoup
from flask import Flask
from threading import Thread

# Telegram настройки
TOKEN = '7683066723:AAHot2507_9RrkpNCMh5QKLi0cQr7cPEVH8'
CHAT_ID = '5305138065'

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

# Проверка Binance
def check_binance():
    sent = load_sent_binance()
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        url = 'https://www.binance.com/bapi/composite/v1/public/cms/article/list/query?type=1&pageNo=1&pageSize=10'
        response = requests.get(url, headers=headers)
        text = response.text
        logging.info(f"Binance raw response: {text[:500]}")  # Логируем первые 500 символов

        data = response.json()  # Если здесь ошибка, значит ответ не JSON

        new_sent = set(sent)

        for article in data.get('data', {}).get('articles', []):
            title = article.get('title', '')
            if 'will list' in title.lower() and title not in sent:
                send_telegram_message(f'📢 Binance Listing: {title}')
                new_sent.add(title)

        save_sent_binance(new_sent)
    except Exception as e:
        logging.warning(f'⚠️ Ошибка Binance: {e}')


# Проверка Upbit (упрощённая, добавь свою реализацию при необходимости)
def check_upbit():
    pass

# Проверка Coinbase (упрощённая)
def check_coinbase():
    pass

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


