# trend.py --- Solana NFT トレンド通知（高頻度通知版）
import requests
import time
from telegram import Bot
import os

# ======== Telegram 設定 ========
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_IDS = os.getenv("TELEGRAM_CHAT_IDS", "")
CHAT_IDS = [cid.strip() for cid in TELEGRAM_CHAT_IDS.split(",") if cid.strip()]

bot = Bot(token=TELEGRAM_TOKEN)


# ======== MagicEden API ========
def get_floor_price(symbol):
    """
    MagicEden floor price API
    """
    url = f"https://api-mainnet.magiceden.dev/v2/collections/{symbol}/stats"
    headers = {"accept": "application/json"}

    try:
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code != 200:
            print(f"[ERROR] API ステータスコード異常 {symbol}: {r.status_code}")
            return None

        data = r.json()
        return data.get("floorPrice")  # lamports（1e9 = 1 SOL）

    except Exception as e:
        print(f"[ERROR] API 取得失敗 ({symbol}): {e}")
        return None


# ======== 通知送信 ========
def send_telegram(message):
    """複数チャットIDへ送信"""
    for cid in CHAT_IDS:
        try:
            bot.send_message(chat_id=cid, text=message)
        except Exception as e:
            print(f"[Telegram ERROR] {e}")


# ======== 前回価格を保存 ========
_last_price = {}


# ======== トレンドチェック ========
def check_trend(label, symbol):
    global _last_price

    floor_lamports = get_floor_price(symbol)
    if floor_lamports is None:
        print(f"[{label}] 価格取得失敗")
        return

    # lamports → SOL
    floor_sol = floor_lamports / 1_000_000_000

    # 初回データ記録
    if symbol not in _last_price:
        _last_price[symbol] = floor_sol
        print(f"[{label}] 初期取得 → {floor_sol:.3f} SOL")
        return

    old = _last_price[symbol]
    diff = floor_sol - old

    # 変動幅（通知頻度操作）========================
    THRESHOLD = 0.05  # ★ 0.05 SOLの増減で通知（高頻度）
    # ===========================================

    # 判定
    status = "HOLD（通知なし）"

    if diff >= THRESHOLD:
        status = f"📈 **売り時チャンス！**\n{label} が **+{diff:.3f} SOL** 上昇！"

    elif diff <= -THRESHOLD:
        status = f"📉 **買い時チャンス！**\n{label} が **{diff:.3f} SOL** 下落！"

    print(f"[{label}] 変動 {diff:.3f} SOL → {status}")

    # 通知条件
    if abs(diff) >= THRESHOLD:
        msg = f"""
🔔 Solana NFT 価格変動アラート
━━━━━━━━━━━━━━━
📦 コレクション：{label}
💰 現在価格：{floor_sol:.3f} SOL
📊 変動：{diff:.3f} SOL

⏱️ チャンス発生！
https://magiceden.io/marketplace/{symbol}
"""
        send_telegram(msg.strip())

    # 更新
    _last_price[symbol] = floor_sol
