import time
import requests
from fastapi import FastAPI

# ===============================
# Telegram Settings
# ===============================
TELEGRAM_BOT_TOKEN = "8455133544:AAE_aaQuzWkxgfR4xSTiwJBo8Wf6CXykyeg"
CHAT_ID = "5917411414"
TG_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"


# Telegram送信
def send_telegram(msg: str):
    payload = {
        "chat_id": CHAT_ID,
        "text": msg
    }
    try:
        requests.post(TG_URL, json=payload)
    except Exception as e:
        print("Telegram Error:", e)


# ===============================
# トレンド検知ロジック（trend.py）を呼び出す
# ===============================
from trend import check_trend  # ←後で trend.py を作成する


app = FastAPI()


@app.get("/")
def root():
    return {"status": "NFT Trend Tool Running"}


# ===============================
# Render の scheduler が叩くエンドポイント
# ===============================
@app.get("/cron")
def cron_job():
    """
    毎回実行される処理
    ① 監視コレクションをループする
    ② トレンド変動をチェック
    ③ 必要なら Telegram に通知
    """

    COLLECTIONS = [
        "basedponks",
        "mocaverse",
        "milady",
        # ←好きなコレクションをもっと追加してOK
    ]

    results = {}

    for col in COLLECTIONS:
        trend_msg = check_trend(col)   # ←後で作る
        results[col] = trend_msg

        # 何か変化があったら通知
        if trend_msg:
            send_telegram(f"🚨 {col} に変動あり！\n{trend_msg}")

        time.sleep(1)

    return {"detail": "Trend checked", "results": results}
    # ===== Cron endpoint =====
from fastapi import FastAPI
from trend import check_trend

app = FastAPI()

@app.get("/cron")
def run_cron():
    # ここにあなたが監視したいコレクションを追加するだけ！
    target_collections = [
        "basedponkz",
        "yourfavoritecollection"
    ]

    for col in target_collections:
        check_trend(col)

    return {"status": "ok", "checked": target_collections}

@app.get("/test")
def test():
    send_telegram_message("📢 テスト通知：Telegram設定は正常です！")
    return {"status": "test sent"}

