# trend.py --- トレンド判定 & Telegram 通知（Magic Eden 版・完成形）

from solana import get_floor_price
from telegram import send_telegram_message

# 前回価格を保存しておくキャッシュ（サーバーが生きている間は保持される）
latest_price_cache: dict[str, float] = {}


def check_trend(
    collection_label: str,
    collection_symbol: str,
    buy_threshold_percent: float = -3.0,
    sell_threshold_percent: float = 5.0,
):
    """
    1コレクション分のトレンド判定を行い、BUY/SELL シグナルが出たら Telegram に通知する。
    """

    global latest_price_cache

    # ① 最新のフロア価格を取得（SOL）
    current_price = get_floor_price(collection_symbol)
    if current_price is None:
        print(f"[Error] {collection_label}: floorPrice が取得できませんでした。")
        return "HOLD"

    # ② 前回価格を取得（初回のみ None）
    prev_price = latest_price_cache.get(collection_symbol)

    # ③ キャッシュ更新（次回比較用）
    latest_price_cache[collection_symbol] = current_price

    # ★ 初回は比較できないので通知なし
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

    # ================================
    #   BUY 通知（Magic Eden ボタン）
    # ================================
    if signal == "BUY":
        msg = (
            f"🚀 <b>BUY シグナルを検出</b>（押し目チャンス）\n\n"
            f"<b>◆ コレクション：</b> {collection_label}\n"
            f"<b>◆ 前回：</b> {prev_price:.3f} SOL\n"
            f"<b>◆ 現在：</b> {current_price:.3f} SOL\n"
            f"<b>◆ 変動率：</b> {change_percent:+.2f}%\n\n"
            f"<a href='https://magiceden.io/marketplace/{collection_symbol}'>🛒 今すぐ買う（BUY）</a>\n\n"
            f"⚠ 投資助言ではありません。最終判断はご自身で。"
        )

        send_telegram_message(msg)
        print(f"[{collection_label}] BUY 通知を送信しました。")
        return "BUY"

    # ================================
    #   SELL 通知（Magic Eden ボタン）
    # ================================
    if signal == "SELL":
        msg = (
            f"💰 <b>SELL シグナルを検出</b>（利確ポイント）\n\n"
            f"<b>◆ コレクション：</b> {collection_label}\n"
            f"<b>◆ 前回：</b> {prev_price:.3f} SOL\n"
            f"<b>◆ 現在：</b> {current_price:.3f} SOL\n"
            f"<b>◆ 変動率：</b> {change_percent:+.2f}%\n\n"
            f"<a href='https://magiceden.io/marketplace/{collection_symbol}?filter=sell'>📤 今すぐ売る（SELL）</a>\n\n"
            f"⚠ 投資助言ではありません。最終判断はご自身で。"
        )

        send_telegram_message(msg)
        print(f"[{collection_label}] SELL 通知を送信しました。")
        return "SELL"

    # ================================
    #   HOLD（通知なし）
    # ================================
    print(f"[{collection_label}] 変動 {change_percent:+.2f}% → HOLD（通知なし）")
    return "HOLD"

