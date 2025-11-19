from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import PlainTextResponse
import hmac, hashlib, base64, json, requests

from config import LINE_CHANNEL_SECRET, LINE_CHANNEL_ACCESS_TOKEN, INVITE_CODE
from db import SessionLocal, init_db, User

app = FastAPI()

@app.on_event("startup")
def startup():
    init_db()

def validate_signature(body: bytes, signature: str) -> bool:
    mac = hmac.new(LINE_CHANNEL_SECRET.encode(), body, hashlib.sha256)
    expected = base64.b64encode(mac.digest()).decode()
    return hmac.compare_digest(expected, signature)

def reply_message(reply_token: str, text: str):
    url = "https://api.line.me/v2/bot/message/reply"
    headers = {"Content-Type": "application/json",
               "Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}"}
    payload = {"replyToken": reply_token,
               "messages": [{"type": "text", "text": text}]}
    requests.post(url, headers=headers, json=payload)

def push_message(uid: str, text: str):
    url = "https://api.line.me/v2/bot/message/push"
    headers = {"Content-Type": "application/json",
               "Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}"}
    payload = {"to": uid,
               "messages": [{"type": "text", "text": text}]}
    requests.post(url, headers=headers, json=payload)

@app.post("/webhook/line", response_class=PlainTextResponse)
async def webhook(request: Request):
    body = await request.body()
    sig = request.headers.get("x-line-signature", "")

    if not validate_signature(body, sig):
        raise HTTPException(status_code=400, detail="Signature error")

    data = json.loads(body.decode())
    db = SessionLocal()

    for ev in data.get("events", []):
        if ev["type"] == "message" and ev["message"]["type"] == "text":
            text = ev["message"]["text"]
            uid = ev["source"]["userId"]
            reply = ev["replyToken"]

            if text == INVITE_CODE:
                exist = db.query(User).filter(User.line_user_id == uid).first()
                if exist:
                    reply_message(reply, "✅すでに登録済みです。通知を送ります。")
                else:
                    db.add(User(line_user_id=uid))
                    db.commit()
                    reply_message(reply, "✅ 登録完了！通知を受け取れるようになりました。")
            else:
                reply_message(reply, "合言葉を送ってください。")

    db.close()
    return "OK"

@app.post("/test/push", response_class=PlainTextResponse)
def test_push():
    db = SessionLocal()
    users = db.query(User).filter(User.is_active == True).all()
    for u in users:
        push_message(u.line_user_id, "テスト通知です")
    return f"Sent to {len(users)} users"
