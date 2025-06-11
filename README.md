
# Telegram бот: Отслеживание листингов (Binance, Upbit, Coinbase)

## Установка

1. Установите зависимости:
```
pip install -r requirements.txt
```

2. Установите переменные окружения:
- `BOT_TOKEN` — токен вашего Telegram-бота
- `CHAT_ID` — ваш chat ID

Можно задать через терминал:
```
export BOT_TOKEN=ВАШ_ТОКЕН
export CHAT_ID=ВАШ_CHAT_ID
```

3. Запустите бота:
```
python bot.py
```

Бот будет каждые 5 минут проверять биржи и присылать уведомления о предстоящих листингах.
