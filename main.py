# main.py --- Solana NFT トレンド監視ツール（管理画面つき・複数ユーザー通知版）

from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
import uvicorn
import asyncio
from telegram_utils import Bot
from trend import check_trend
from config import TELEGRAM_CHAT_IDS

app = FastAPI()

# ==========================
#   監視コレクション一覧
# ==========================
COLLECTIONS = [
    ("Froganas", "froganas"),
    ("Oogy", "oogy"),
    ("Liberty Square", "liberty_square"),
]

# ==========================
#   管理画面のHTML
# ==========================
def render_dashboard():
    html = f"""
    <html>
        <head>
            <title>NFT Trend Tool Admin</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    background-color: #111;
                    color: #fff;
                    padding: 40px;
                }}
                h1 {{
                    font-size: 28px;
                    font-weight: bold;
                    margin-bottom: 20px;
                }}
                .card {{
                    background: #1e1e1e;
                    padding: 20px;
                    border-radius: 12px;
                    margin-bottom: 25px;
                }}
                input {{
                    padding: 10px;
                    width: 280px;
                    border-radius: 6px;
                    border: none;
                }}
                button {{
                    background: #4F8BFF;
                    color: white;
                    border: none;
                    padding: 10px 18px;
                    border-radius: 6px;
                    cursor: pointer;
                    margin-left: 5px;
                }}
                button:hover {{
                    background: #1f5fe0;
                }}
                .chat-item {{
                    margin: 5px 0;
                    padding: 8px 12px;
                    background: #222;
                    border-radius: 6px;
                }}
            </style>
        </head>
        <body>

            <h1>NFT トレンド通知ツール - 管理画面</h1>

            <div class="card">
                <h2>登録済みチャットID一覧</h2>
                {"".join([f'<div class="chat-item">{cid}</div>' for cid in TELEGRAM_CHAT_IDS])}
            </div>

            <div class="card">
                <h2>新規チャットIDを登録</h2>
                <form action="/add_user" method="post">
                    <input name="chat_id" placeholder="例：5917411414" required>
                    <button type="submit">追加</button>
                </form>
            </div>

            <div class="card">
                <h2>テスト通知を送信</h2>
                <form action="/test_notify" method="post">
                    <button type="submit">全ユーザーへ送信</button>
                </form>
            </div>

        </body>
    </html>
    """
    return html


# ==========================
#   トレンド監視ループ
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

        print("===== チェック完了 → 次の計測まで待機します =====")
        await asyncio.sleep(60 * 5)  # ← 本番では5分おき


# ==========================
#   手動 trigger
# ==========================
@app.get("/cron")
async def run_manual():
    print("[CRON] Manual trigger received.")
    for label, symbol in COLLECTIONS:
        check_trend(label, symbol)
    return {"status": "OK"}


# ==========================
#   管理画面
# ==========================
@app.get("/", response_class=HTMLResponse)
async def dashboard():
    return render_dashboard()


# ==========================
#   新規チャットID登録
# ==========================
@app.post("/add_user")
async def add_user(chat_id: str = Form(...)):
    with open("user_list.txt", "a") as f:
        f.write(chat_id + "\n")

    return HTMLResponse(
        "<h2>登録完了しました！</h2><a href='/'>戻る</a>"
    )


# ==========================
#   テスト通知
# ==========================
@app.post("/test_notify")
async def test_notify():
    from telegram import send_telegram_message

    for cid in TELEGRAM_CHAT_IDS:
        send_telegram_message("🔔 テスト通知です")

    return HTMLResponse(
        "<h2>送信しました！</h2><a href='/'>戻る</a>"
    )


# ==========================
#   起動
# ==========================
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(trend_loop())
    uvicorn.run(app, host="0.0.0.0", port=10000)
