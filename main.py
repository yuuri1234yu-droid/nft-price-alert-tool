# main.py --- Solana NFT トレンド監視ツール（3コレクション版）
from fastapi import FastAPI
import uvicorn
import asyncio

from trend import check_trend

app = FastAPI()

# ==========================
#   監視コレクション一覧（3つだけ）
# ==========================
COLLECTIONS = [
    ("Froganas", "froganas"),
    ("Oogy", "oogy"),
    ("Liberty Square", "liberty_square"),
]

# ==========================
#   監視ループ（5〜15分ごと）
# ==========================
async def trend_loop():
    print("=== Solana NFT Trend Tool Started ===")

    while True:
        print("\n===== Checking Solana Collections =====")

        for label, symbol in COLLECTIONS:
            try:
                print(f"--- {label} ({symbol}) をチェック中 ---")
                check_trend(label, symbol)

            except Exception as e:
                print(f"[ERROR] {label} の処理中に問題: {e}")

        print("===== チェック完了。次の計測まで待機します =====")

        await asyncio.sleep(60 * 5)  # 5分ごとに実行（推奨）

# ==========================
#   /cron エンドポイント
# ==========================
@app.get("/cron")
async def run_manual():
    print("[CRON] Manual trigger received.")
    for label, symbol in COLLECTIONS:
        check_trend(label, symbol)

    return {"status": "NFT Trend Tool (Solana) Running"}

# ==========================
#   メイン起動
# ==========================
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(trend_loop())
    uvicorn.run(app, host="0.0.0.0", port=10000)

