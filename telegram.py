# telegram.py --- Telegram 送信用

import requests
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID


def send_telegram_message(text: str):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("[Telegram] トークン or chat_id が設定されていません。")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "HTML",  # 絵文字や改行をキレイに表示
    }

    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"[Telegram] 送信エラー: {e}")
