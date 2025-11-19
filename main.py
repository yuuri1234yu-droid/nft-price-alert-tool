# main.py --- NFT Trend Tool (Solana Edition)

from fastapi import FastAPI
from trend import check_trend

app = FastAPI()

# ===== Solana 監視コレクション一覧 =====
# symbol は Magic Eden の URL スラッグに合わせる
COLLECTIONS = [
    ("Froganas", "froganas"),
    ("Oogy", "oogy"),
    ("Liberty Square", "libertysquare"),
    ("Jelly Rascals", "jellyrascals"),
    ("Boogle", "boogle"),
]


@app.get("/")
def root():
    """動作確認用のルートエンドポイント"""
    return {"status": "NFT Trend Tool (Solana) Running"}


@app.get("/cron")
def cron():
    """
    GitHub Actions または手動アクセスで動く Cron 用エンドポイント。
    全コレクションのトレンドチェックを実行。
    """
    checked = []

    for c in COLLECTIONS:
        label = c["label"]
        symbol = c["symbol"]

        print(f"[CRON] Checking {label} ({symbol})...")

        signal = check_trend(label, symbol)

        checked.append({
            "label": label,
            "symbol": symbol,
            "signal": signal
        })

    return {
        "status": "ok",
        "checked": checked
    }

