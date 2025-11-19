# trend.py --- トレンド判定 & Telegram 通知 

from solana import get_floor_price
from telegram import send_telegram_message

# 前回価格キャッシュ
latest_price_cache: dict[str, float] = {}


def check_trend(
    collection_label: str,
    collection_symbol: str,
    buy_threshold_percent: float = -3.0,   # ← BUY 判定を上げた
    sell_threshold_percent: float = 3.0,   # ← SELL 判定を下げた
):
    """1コレクション分のトレンドチェック"""

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

        msg = (
            f"【{signal} シグナル】{direction_ja}\n"
            f"コレクション：{collection_label}\n"
            f"シンボル　　：{collection_symbol}\n"
            f"\n"
            f"前回フロア　：{prev_price:.3f} SOL\n"
            f"現在フロア　：{current_price:.3f} SOL\n"
            f"変動率　　　：{change_percent:+.2f}%\n"
            f"\n"
            f"🔗 購入/売却リンク\n"
            f"https://magiceden.io/marketplace/{collection_symbol}\n"
            f"\n"
            f"※判断はご自身でお願いします。"
        )

        send_telegram_message(msg)
        print(f"[{collection_label}] {signal} 通知を送信しました。")

    else:
        print(
            f"[{collection_label}] 変動 {change_percent:+.2f}% → HOLD（通知なし）"
        )

    return signal


