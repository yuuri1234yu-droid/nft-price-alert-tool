# trend.py --- トレンド判定 & Telegram 通知

from solana import get_floor_price
from telegram import send_telegram_message

# 前回価格を保存しておくキャッシュ（サーバーが生きている間は保持される）
latest_price_cache: dict[str, float] = {}


def check_trend(
    collection_label: str,
    collection_symbol: str,
    buy_threshold_percent: float = -10.0,
    sell_threshold_percent: float = 15.0,
):
    """
    1コレクション分のトレンド判定を行い、BUY/SELL シグナルが出たら Telegram に通知する。
    """

    global latest_price_cache

    # ① 最新のフロア価格を取得（SOL）
    current_price = get_floor_price(collection_symbol)
    if current_price is None:
        return "HOLD"

    # ② 前回価格を取得（初回だけ None）
    prev_price = latest_price_cache.get(collection_symbol)

    # ③ キャッシュ更新（次回比較用）
    latest_price_cache[collection_symbol] = current_price

    # 前回データがなければ判定できないので終了
    if prev_price is None:
        print(f"[{collection_label}] 初回取得のため判定スキップ: {current_price:.3f} SOL")
        return "HOLD"

    # ④ 変動率を計算
    change_percent = (current_price - prev_price) / prev_price * 100

    # ⑤ BUY / SELL / HOLD 判定
    signal = "HOLD"
    if change_percent <= buy_threshold_percent:
        signal = "BUY"
    elif change_percent >= sell_threshold_percent:
        signal = "SELL"

    # ⑥ 通知が必要なら Telegram 送信
    if signal != "HOLD":
        direction_ja = "買い時（押し目）" if signal == "BUY" else "売り時（利確候補）"

        msg = (
            f"【{signal} シグナル】{direction_ja}\n"
            f"コレクション：{collection_label}\n"
            f"シンボル　　：{collection_symbol}\n"
            f"\n"
            f"前回フロア　：{prev_price:.3f} SOL\n"
            f"現在フロア　：{current_price:.3f} SOL\n"
            f"変動率　　　：{change_percent:+.2f}%\n"
            f"\n"
            f"※この通知は投資助言ではありません。\n"
            f"　エントリー/利確の最終判断はご自身でお願いします。"
        )

        send_telegram_message(msg)
        print(f"[{collection_label}] {signal} 通知を送信しました。")

    else:
        print(
            f"[{collection_label}] 変動 {change_percent:+.2f}% → HOLD（通知なし）"
        )

    return signal
