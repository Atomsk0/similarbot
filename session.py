from telethon.sync import TelegramClient
from telethon.sessions import StringSession

API_ID = "20036987"
API_HASH = "b91bd8943ea55861655b2ece542855a4"

with TelegramClient(StringSession(), API_ID, API_HASH) as client:
    print(client.session.save())
