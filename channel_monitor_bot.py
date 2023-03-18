import logging
import os
from simhash import Simhash
from pyrogram import Client, filters
from python_telegram_bot import Updater

API_ID = "your_api_id"
API_HASH = "your_api_hash"
BOT_TOKEN = "your_bot_token"

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize Pyrogram Client
app = Client("channel_monitor_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Initialize python-telegram-bot Updater
updater = Updater(token=BOT_TOKEN, use_context=True)

# The monitored channels and the target channel
monitored_channels = set()
target_channel = "@your_target_channel"

# A set to store Simhash values of previous messages
simhash_set = set()

# Define the similarity threshold (0 to 64)
similarity_threshold = 10

def add_channel(update, context):
    channel_link = update.message.text
    if channel_link.startswith("https://t.me/"):
        channel_username = channel_link[13:]
        monitored_channels.add(channel_username)
        update.message.reply_text(f"Added {channel_username} to monitored channels.")
    else:
        update.message.reply_text("Please provide a valid Telegram channel link.")

def simhash_similarity(a, b):
    return a.distance(b)

@app.on_message(filters.text & filters.channel)
async def handle_channel_post(client, message):
    if message.chat.username in monitored_channels:
        message_text = message.text or message.caption
        if message_text:
            message_simhash = Simhash(message_text)

            for stored_simhash in simhash_set:
                if simhash_similarity(stored_simhash, message_simhash) <= similarity_threshold:
                    return

            simhash_set.add(message_simhash)

            await client.forward_messages(
                chat_id=target_channel,
                from_chat_id=message.chat.id,
                message_ids=message.message_id
            )

def main():
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("addchannel", add_channel))

    updater.start_polling()
    app.run()

if __name__ == '__main__':
    main()
