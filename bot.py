import requests
import time
import os
import logging
import threading
from flask import Flask

# Настройки Telegram
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# Настройка логгера
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Flask сервер для Render
app = Flask(__name__)

@app.route("/")
def home():
    return "🤖 Listing bot is running!"

def send_telegram_message(text):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        data = {"chat_id": CHAT_ID, "text": text}
        response = requests.post(url, json=data)
        if response.status_code != 200:
            logging.warning(f"Ошибка отправки в Telegram: {response.text}")
    except Exception as e:
        logging.error(f"Telegram Error: {e}")

def check_binance():
    logging.info("📡 Проверка Binance...")
    try:
        url = "https://api.binance.com/api/v3/exchangeInfo"
        response = requests.get(url)
        data = response.json()
        # Пример фильтрации
        symbols = [s["symbol"] for s in data["symbols"] if s["status"] == "TRADING"]
        return symbols
    except Exception as e:
        logging.warning(f"Ошибка Binance: {e}")
        return []

def check_upbit():
    logging.info("📡 Проверка Upbit...")
    try:
        url = "https://api.upbit.com/v1/market/all"
        response = requests.get(url)
        data = response.json()
        symbols = [item["market"] for item in data if item["market"].startswith("KRW-")]
        return symbols
    except Exception as e:
        logging.warning(f"Ошибка Upbit: {e}")
        return []

def check_coinbase():
    logging.info("📡 Проверка Coinbase...")
    try:
        url = "https://api.exchange.coinbase.com/products"
        headers = {"User-Agent": "ListingBot/1.0"}
        response = requests.get(url, headers=headers)
        data = response.json()
        symbols = [item["id"] for item in data]
        return symbols
    except Exception as e:
        logging.warning(f"Ошибка Coinbase: {e}")
        return []

# Хранение уже известных символов
known = {
    "binance": set(),
    "upbit": set(),
    "coinbase": set()
}

def monitor_listings():
    global known
    while True:
        try:
            new_binance = set(check_binance())
            new_upbit = set(check_upbit())
            new_coinbase = set(check_coinbase())

            # Binance
            added_binance = new_binance - known["binance"]
            if added_binance:
                for s in added_binance:
                    send_telegram_message(f"🟢 Новый листинг на Binance: {s}")
                known["binance"] = new_binance

            # Upbit
            added_upbit = new_upbit - known["upbit"]
            if added_upbit:
                for s in added_upbit:
                    send_telegram_message(f"🟢 Новый листинг на Upbit: {s}")
                known["upbit"] = new_upbit

            # Coinbase
            added_coinbase = new_coinbase - known["coinbase"]
            if added_coinbase:
                for s in added_coinbase:
                    send_telegram_message(f"🟢 Новый листинг на Coinbase: {s}")
                known["coinbase"] = new_coinbase

        except Exception as e:
            logging.error(f"❌ Общая ошибка при запуске бота: {e}")
            send_telegram_message(f"❌ Ошибка в Listing Bot: {e}")

        time.sleep(300)  # Проверка каждые 5 минут

def start_bot():
    send_telegram_message("✅ Listing Bot запущен и работает.")
    monitor_listings()

if __name__ == "__main__":
    # Запуск Flask в отдельном потоке
    port = int(os.environ.get("PORT", 10000))
    threading.Thread(target=lambda: app.run(host="0.0.0.0", port=port)).start()
    # Запуск логики бота
    start_bot()
