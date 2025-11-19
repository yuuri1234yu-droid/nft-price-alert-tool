# telegram.py --- 複数ユーザーに通知送信

import requests
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_IDS


def send_telegram_message(text: str):
    if not TELEGRAM_BOT_TOKEN:
        print("[Telegram] BOT TOKEN が設定されていません。")
        return

    if not TELEGRAM_CHAT_IDS:
        print("[Telegram] TELEGRAM_CHAT_IDS が空です。")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

    # 全員に送信
    for cid in TELEGRAM_CHAT_IDS:
        payload = {
            "chat_id": cid,
            "text": text,
            "parse_mode": "HTML",
        }

        try:
            r = requests.post(url, json=payload, timeout=10)
            if r.status_code != 200:
                print(f"[Telegram] 送信エラー({cid}): {r.text}")
        except Exception as e:
            print(f"[Telegram] 例外エラー({cid}): {e}")

    print(f"[Telegram] {len(TELEGRAM_CHAT_IDS)} 件に通知を送信しました。")
