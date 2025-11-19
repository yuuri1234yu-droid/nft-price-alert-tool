import time
from fastapi import FastAPI
from trend import check_trend

app = FastAPI()

# 監視したいコレクション
COLLECTIONS = ["basedponkz", "mocaverse", "milady"]  # ← 好きに追加OK

@app.get("/")
def root():
    return {"status": "NFT Trend Tool Running"}

# Render の cron (Scheduler) が毎分ここを叩く
@app.get("/cron")
def cron():
    for c in COLLECTIONS:
        check_trend(c)
    return {"detail": "Trend checked"}

    for u in users:
        push_message(u.line_user_id, "テスト通知です")
    return f"Sent to {len(users)} users"
