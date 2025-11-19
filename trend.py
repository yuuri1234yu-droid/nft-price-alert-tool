# trend.py --- Solana NFT トレンド監視（Telegram通知対応）
import requests
import os
from telegram import send_message

# Magic Eden API
BASE_URL = "https://api-mainnet.magiceden.dev/v2/collections/{symbol}/stats"

# Telegram Chat IDs（カンマ区切り）
CHAT_IDS = os.getenv("TELEGRAM_CHAT_IDS", "").split(",")


# -----------------------------------------------------
# 通知送信用のラッパー関数
# -----------------------------------------------------
def notify(text):
    """
    全ての Telegram チャットに送信する
    """
    for cid in CHAT_IDS:
        cid = cid.strip()
        if cid:
            try:
                send_message(cid, text)
                print(f"[Telegram] Notified → {cid}")
            except Exception as e:
                print(f"[Telegram ERROR] {e}")


# -----------------------------------------------------
# MagicEden API から floorPrice / listedCount を取得
# -----------------------------------------------------
def fetch_stats(symbol):
    url = BASE_URL.format(symbol=symbol)
    r = requests.get(url)

    if r.status_code != 200:
        print(f"[ERROR] APIエラー {symbol}: {r.status_code}")
        return None

    return r.json()


# -----------------------------------------------------
# トレンド判定ロジック（通知を出す）
# -----------------------------------------------------
# 過去の floor を保存（前回値と比較するため）
last_floor = {}

def check_trend(label, symbol):
    """
    変動率で売り時・買い時を通知する
    """
    global last_floor

    data = fetch_stats(symbol)
    if data is None:
        return

    # floorPrice を SOL に変換（Magic Eden は 1e9）
    if "floorPrice" not in data or data["floorPrice"] == 0:
        print(f"[{label}] floorPrice が取得できなかったためスキップ")
        return

    floor = data["floorPrice"] / 1e9
    listed = data.get("listedCount", 0)

    print(f"[{label}] 現在 floor={floor} SOL, 出品数={listed}")

    # 初回取得 → 記録だけして終了
    if symbol not in last_floor:
        last_floor[symbol] = floor
        print(f"[{label}] 初回取得のため変動チェックなし")
        return

    before = last_floor[symbol]
    change = ((floor - before) / before) * 100  # 変動率 %

    print(f"[{label}] 変動率={change:.2f}%")

    # -----------------------------------------------------
    # 🔥 通知ロジック（より変動性を強く → 通知が来やすい）
    # -----------------------------------------------------

    # ▼ 強烈な買い時（急落）
    if change <= -3:
        notify(f"🔻【買い時チャンス】{label}\nfloor: {floor:.3f} SOL\n変動: {change:.2f}%\n出品数: {listed}")

    # ▼ 買い時（軽い下落）
    elif change <= -1.0:
        notify(f"📉【買い時の兆し】{label}\nfloor: {floor:.3f} SOL\n変動: {change:.2f}%\n出品数: {listed}")

    # ▼ 強烈な売り時（急騰）
    elif change >= 3:
        notify(f"🚀【売り時チャンス】{label}\nfloor: {floor:.3f} SOL\n変動: +{change:.2f}%\n出品数: {listed}")

    # ▼ 売り時（軽い上昇）
    elif change >= 1.0:
        notify(f"📈【売り時の兆し】{label}\nfloor: {floor:.3f} SOL\n変動: +{change:.2f}%\n出品数: {listed}")

    # 前回値を更新
    last_floor[symbol] = floor

