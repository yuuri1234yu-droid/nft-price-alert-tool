# trend.py --- トレンド判定 & Telegram 通知（floor商品リンク版）

from solana import get_floor_price
from telegram import send_telegram_message
import requests

# 前回価格キャッシュ
latest_price_cache: dict[str, float] = {}


def get_floor_item(symbol: str):
    """
    Magic Eden の最安1件（floor item）を取得する
    """
    url = f"https://api-mainnet.magiceden.dev/v2/collections/{symbol}/listings?offset=0&limit=1&sort=price+asc"

    try:
        r = requests.get(url, timeout=10)
        data = r.json()

        if not isinstance(data, list) or len(data) == 0:
            print(f"[{symbol}] floor item が取得できませんでした: {data}")
            return None

        item = data[0]

        token_mint = item.get("tokenMint")
        lamports_price = item.get("price", 0)
        sol_price = lamports_price / 1_000_000_000

        item_url = f"https://magiceden.io/item-details/{token_mint}"

        return {
            "token_mint": token_mint,
            "price": sol_price,
            "url": item_url
        }

    except Exception as e:
        print(f"[ERROR] floor取得失敗 ({symbol}): {e}")
        return None



def check_trend(
    collection_label: str,
    collection_symbol: str,
    buy_threshold_percent: float = -0.3,   # BUY判定
    sell_threshold_percent: float = 0.3,    # SELL判定
):

    global latest_price_cache

    # ① 現在価格取得
    current_price = get_floor_price(collection_symbol)
    if current_price is None:
        return "HOLD"

    # ② 前回価格取得
    prev_price = latest_price_cache.get(collection_symbol)

    # ③ キャッシュ更新
    latest_price_cache[collection_symbol] = current_price

    if prev_price is None:
        print(f"[{collection_label}] 初回取得 → 判定スキップ: {current_price:.3f} SOL")
        return "HOLD"

    # ④ 変動率
    change_percent = (current_price - prev_price) / prev_price * 100

    # ⑤ 判定
    signal = "HOLD"
    if change_percent <= buy_threshold_percent:
        signal = "BUY"
    elif change_percent >= sell_threshold_percent:
        signal = "SELL"

    # ⑥ 通知
    if signal != "HOLD":
        direction_ja = "買い時（押し目）" if signal == "BUY" else "売り時（利確チャンス）"

        # 🌟 floorアイテムを取得（これが今回の大改造）
        floor_item = get_floor_item(collection_symbol)

        if floor_item:
            item_url = floor_item["url"]
            item_price = floor_item["price"]
        else:
            # fallback：通常のコレクションページ
            item_url = f"https://magiceden.io/marketplace/{collection_symbol}"
            item_price = current_price

        msg = (
            f"【{signal} シグナル】{direction_ja}\n"
            f"コレクション：{collection_label}\n"
            f"シンボル　　：{collection_symbol}\n"
            f"\n"
            f"前回フロア　：{prev_price:.3f} SOL\n"
            f"現在フロア　：{current_price:.3f} SOL\n"
            f"変動率　　　：{change_percent:+.2f}%\n"
            f"\n"
            f"🌟 最安アイテム　：{item_price:.3f} SOL\n"
            f"🔗 いますぐ購入\n"
            f"{item_url}\n"
            f"\n"
            f"※判断はご自身でお願いします。"
        )

        send_telegram_message(msg)
        print(f"[{collection_label}] {signal} 通知を送信しました。（floor item 送信）")

    else:
        print(f"[{collection_label}] 変動 {change_percent:+.2f}% → HOLD（通知なし）")

    return signal



