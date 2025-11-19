from opensea import get_floor_price
from telegram import send_telegram_message

# 過去の価格を保持する変数（サーバー再起動でリセット）
latest_price_cache = {}

def check_trend(collection_slug: str, threshold_percent: float = 5):
    global latest_price_cache

    new_price = get_floor_price(collection_slug)
    if new_price is None:
        return

    old_price = latest_price_cache.get(collection_slug)

    if old_price:
        diff = ((new_price - old_price) / old_price) * 100

        if abs(diff) >= threshold_percent:
            direction = "⬆ 上昇" if diff > 0 else "⬇ 下落"
            send_telegram_message(
                f"📈 <b>{collection_slug}</b>\n"
                f"{direction} {diff:.2f}%\n"
                f"Old: {old_price}\n"
                f"New: {new_price}"
            )

    latest_price_cache[collection_slug] = new_price
