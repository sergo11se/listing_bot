import requests
import time
import os
import logging
from bs4 import BeautifulSoup
from flask import Flask

TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
SEND_URL = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

app = Flask(__name__)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

last_binance = None
last_upbit = None
last_coinbase = None

def send_telegram(msg):
    try:
        response = requests.post(SEND_URL, data={"chat_id": CHAT_ID, "text": msg})
        if response.status_code != 200:
            logging.warning(f"Telegram error: {response.text}")
    except Exception as e:
        logging.error(f"Failed to send message to Telegram: {e}")

def check_binance():
    global last_binance
    try:
        url = "https://www.binance.com/en/support/announcement/c-48"
        html = requests.get(url).text
        soup = BeautifulSoup(html, "html.parser")
        article = soup.find("a", class_="css-1ej4hfo")
        if article:
            title = article.text.strip()
            link = "https://www.binance.com" + article.get("href")
            if title != last_binance and "Will List" in title:
                last_binance = title
                send_telegram(f"🟢 Новый листинг на Binance: {title}\n{link}")
    except Exception as e:
        logging.error(f"Binance error: {e}")

def check_upbit():
    global last_upbit
    try:
        url = "https://upbit.com/service_center/notice"
        html = requests.get(url).text
        soup = BeautifulSoup(html, "html.parser")
        notice = soup.select_one(".notice-list a")
        if notice:
            title = notice.text.strip()
            link = "https://upbit.com" + notice.get("href")
            if title != last_upbit and ("거래지원" in title or "상장" in title):
                last_upbit = title
                send_telegram(f"🟢 Новый листинг на Upbit: {title}\n{link}")
    except Exception as e:
        logging.error(f"Upbit error: {e}")

def check_coinbase():
    global last_coinbase
    try:
        url = "https://www.coinbase.com/asset-directory"
        html = requests.get(url).text
        soup = BeautifulSoup(html, "html.parser")
        assets = soup.find_all("a", class_="cds-asset-link")
        if assets:
            name = assets[0].text.strip()
            link = "https://www.coinbase.com" + assets[0].get("href")
            if name != last_coinbase:
                last_coinbase = name
                send_telegram(f"🟢 Возможно новое добавление на Coinbase: {name}\n{link}")
    except Exception as e:
        logging.error(f"Coinbase error: {e}")

@app.route("/")
def home():
    return "Listing bot is running."

if __name__ == "__main__":
    send_telegram("✅ Бот запущен и следит за листингами.")
    while True:
        logging.info("📡 Проверка Binance...")
        check_binance()
        logging.info("📡 Проверка Upbit...")
        check_upbit()
        logging.info("📡 Проверка Coinbase...")
        check_coinbase()
        time.sleep(300)  # 5 минут

