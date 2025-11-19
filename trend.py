# trend.py --- トレンド判定 & Telegram通知（requestsのみ）

import requests
from os import getenv

from solana import get_floor_price

# 環境変数から取得（Render の Environment に設定済み）
BOT_TOKEN = getenv("TELEGRAM_TOKEN", "")
CHAT_IDS = getenv("TELEGRAM_CHAT_IDS", "")

# 送信用URL
def send_telegram_message(text: str):
    if not BOT_TOKEN or not CHAT_IDS:
        print("[Telegram] トークン or チャットID が未設定です")
        return

    for chat_id in CHAT_IDS.split(","):
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {"chat_id": chat_id.strip(), "text": text}
        try:
            requests.post(url, json=payload, timeout=10)
        except Exception as e:
            print(f"[Telegram] エラー: {e}")


# 価格キャッシュ
latest_price_cache: dict[str, float] = {}


def check_trend(
    collection_label: str,
    collection_symbol: str,
    buy_threshold_percent: float = -0.5,  # 1%下落でBUY
    sell_threshold_percent: float = 0.5,  # 1%上昇でSELL
):
    """
    シンプル変動通知モデル
    """

    global latest_price_cache

    # ① 最新のフロア価格を取得
    current_price = get_floor_price(collection_symbol)
    if current_price is None:
        return "HOLD"

    # ② 前回価格
    prev_price = latest_price_cache.get(collection_symbol)

    # ③ キャッシュ更新（次回比較用）
    latest_price_cache[collection_symbol] = current_price

    # 初回は比較不可
    if prev_price is None:
        print(f"[{collection_label}] 初回価格 {current_price:.3f} SOL")
        return "HOLD"

    # ④ 変動率を計算
    change_percent = (current_price - prev_price) / prev_price * 100

    # 判定
    signal = "HOLD"
    if change_percent <= buy_threshold_percent:
        signal = "BUY"
    elif change_percent >= sell_threshold_percent:
        signal = "SELL"

    # ⑤ 通知
    if signal != "HOLD":
        msg = (
            f"【{signal}】 {collection_label}\n"
            f"前回: {prev_price:.3f} SOL\n"
            f"現在: {current_price:.3f} SOL\n"
            f"変動: {change_percent:+.2f}%\n"
        )
        send_telegram_message(msg)
        print(f"[{collection_label}] {signal} 通知送信済み")
    else:
        print(f"[{collection_label}] {change_percent:+.2f}% → HOLD")

    return signal


    # 前回値を更新
    last_floor[symbol] = floor

