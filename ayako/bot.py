
from hydrogram import Client

from .config import API_HASH, API_ID, BOT_TOKEN

Ayako = Client(
    name="AyakoRobot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    sleep_threshold=180,
    in_memory=True,
    workers=16,
)