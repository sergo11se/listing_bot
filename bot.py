
import os
import time
import requests
from datetime import datetime
from bs4 import BeautifulSoup

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

sent_announcements = set()

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "HTML"}
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print(f"Ошибка отправки Telegram-сообщения: {e}")

def fetch_binance():
    url = "https://www.binance.com/en/support/announcement"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    for a in soup.select("a"):
        if "/en/support/announcement/" in a.get("href", "") and "Will List" in a.text:
            title = a.text.strip()
            link = "https://www.binance.com" + a["href"]
            if link not in sent_announcements:
                sent_announcements.add(link)
                send_telegram_message(f"🟢 <b>[Binance]</b> Новый листинг:
<b>{title}</b>
🔗 {link}")

def fetch_upbit():
    url = "https://api-manager.upbit.com/api/v1/notices?region=global"
    response = requests.get(url).json()
    for item in response.get("data", []):
        title = item["title"]
        if "New digital asset" in title or "Listing" in title:
            link = f"https://upbit.com/service_center/notice?id={item['id']}"
            if link not in sent_announcements:
                sent_announcements.add(link)
                send_telegram_message(f"🟢 <b>[Upbit]</b> {title}
🔗 {link}")

def fetch_coinbase():
    url = "https://api.exchange.coinbase.com/assets"
    response = requests.get(url).json()
    for asset in response:
        if asset.get("status") == "new":
            name = asset.get("name", "")
            id_ = asset.get("id", "")
            link = f"https://www.coinbase.com/price/{id_.lower()}"
            if link not in sent_announcements:
                sent_announcements.add(link)
                send_telegram_message(f"🟢 <b>[Coinbase]</b> Новый актив:
<b>{name}</b>
🔗 {link}")

def start_message():
    send_telegram_message(
        "🤖 Бот успешно запущен!
"
        "Следим за листингами на: Binance, Upbit, Coinbase
"
        "⏰ Проверка каждые 5 минут."
    )

def run():
    start_message()
    while True:
        try:
            fetch_binance()
            fetch_upbit()
            fetch_coinbase()
        except Exception as e:
            print(f"Ошибка при обновлении: {e}")
        time.sleep(300)

if __name__ == "__main__":
    run()
