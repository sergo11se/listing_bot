import requests
import time
import json
import os
import logging
from bs4 import BeautifulSoup
from flask import Flask

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Настройки Telegram
TELEGRAM_TOKEN = '7683066723:AAHot2507_9RrkpNCMh5QKLi0cQr7cPEVH8'
CHAT_ID = '5305138065'

# Файл для хранения уже отправленных листингов
SENT_FILE = "sent.json"

# Загрузка отправленных листингов
if os.path.exists(SENT_FILE):
    with open(SENT_FILE, "r") as f:
        sent_listings = set(json.load(f))
else:
    sent_listings = set()


def save_sent_listings():
    with open(SENT_FILE, "w") as f:
        json.dump(list(sent_listings), f)


def send_telegram(message):
    url = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage'
    data = {'chat_id': CHAT_ID, 'text': message}
    try:
        response = requests.post(url, data=data)
        if not response.ok:
            logging.warning(f"❌ Ошибка Telegram: {response.text}")
    except Exception as e:
        logging.warning(f"❌ Telegram ошибка: {e}")


def check_binance():
    logging.info("📡 Проверка Binance...")
    try:
        response = requests.get('https://www.binance.com/bapi/composite/v1/public/cms/article/list/query?type=1&pageNo=1&pageSize=10')
        articles = response.json().get("data", {}).get("articles", [])
        for article in articles:
            title = article.get("title", "")
            if "will list" in title.lower():
                symbol = title.split("Will List")[-1].strip().split()[0]
                listing_id = f"binance:{symbol}"
                if listing_id not in sent_listings:
                    send_telegram(f"💥 Новый листинг на Binance: {symbol}")
                    sent_listings.add(listing_id)
                    save_sent_listings()
    except Exception as e:
        logging.warning(f"⚠️ Ошибка Binance: {e}")


def check_upbit():
    logging.info("📡 Проверка Upbit...")
    try:
        response = requests.get('https://upbit.com/service_center/notice')
        soup = BeautifulSoup(response.text, 'html.parser')
        notices = soup.select('a[href^="/service_center/notice"]')
        for notice in notices:
            text = notice.get_text(strip=True)
            if "상장" in text or "리스트" in text:  # 'листинг' на корейском
                link = notice['href']
                listing_id = f"upbit:{link}"
                if listing_id not in sent_listings:
                    send_telegram(f"💥 Новый листинг на Upbit: {text}")
                    sent_listings.add(listing_id)
                    save_sent_listings()
    except Exception as e:
        logging.warning(f"⚠️ Ошибка Upbit: {e}")


def check_coinbase():
    logging.info("📡 Проверка Coinbase...")
    try:
        headers = {"Accept": "application/json"}
        response = requests.get("https://api.coinbase.com/v2/assets/prices?limit=20", headers=headers)
        data = response.json()
        for item in data.get("data", []):
            slug = item.get("slug", "")
            if slug:
                listing_id = f"coinbase:{slug}"
                if listing_id not in sent_listings:
                    send_telegram(f"💥 Новый листинг на Coinbase: {slug}")
                    sent_listings.add(listing_id)
                    save_sent_listings()
    except Exception as e:
        logging.warning(f"⚠️ Coinbase вернул ошибку: {e}")


# Flask для Render ping
app = Flask(__name__)

@app.route("/")
def home():
    return "Listing Bot работает!"


def main_loop():
    while True:
        try:
            check_binance()
            check_upbit()
            check_coinbase()
        except Exception as e:
            logging.error(f"❌ Общая ошибка при запуске бота: {e}")
            send_telegram(f"❌ Бот упал с ошибкой: {e}")
        time.sleep(300)  # 5 минут


if __name__ == "__main__":
    import threading
    threading.Thread(target=main_loop, daemon=True).start()
    app.run(host="0.0.0.0", port=10000)

