# config.py
import os
from dotenv import load_dotenv

load_dotenv()

CHAT_IDS_TEXT = os.getenv("TELEGRAM_CHAT_IDS", "")

# "12345,67890,11111" → ["12345", "67890", "11111"]
TELEGRAM_CHAT_IDS = [cid.strip() for cid in CHAT_IDS_TEXT.split(",") if cid.strip()]

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")

