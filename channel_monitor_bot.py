import logging
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.sync import TelegramClient as UserClient
from telethon.sessions import StringSession
from simhash import Simhash
from telethon import TelegramClient, events

API_ID = "20036987"
API_HASH = "b91bd8943ea55861655b2ece542855a4"
BOT_TOKEN = "6148610901:AAE-E4BCaMIvqxlTcsIiAmD0tGFr1nGqS1Y"
USER_SESSION_STRING = "1ApWapzMBu1awNIIvKVCQ7xxcRxrOHvB_0N9Rb7a-tg3dolA00uZ_2u00hPe-uU1j51Xgk7SqFxFpENE3ZD0lopUImtfV0TrNrQpUYtyw-bFCtBwK8jNl4JJgeUmKDJu7Wc3A3UNg2YlYM3nroa99v7AJYhmqn5-im0ujT5Du_tQSdvqXM_mdDi45ri2B7b-sYAE1dmIhN9Qi2PQptFKXceGcUd76PcK3cpWrsKBI939ug80J6pcUvrWLLurq0Z-YHbgmfauO6kJ2XdDNtnPg_pDCTm-8V59Kj1lVTkYp3cBtdJe-Nr8yafy9Bc6BIp_Lh9rOrMEeEFEV-QHdqRzca2hJOoje828="

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize Telethon Client
client = TelegramClient("new_channel_monitor_bot", api_id=API_ID, api_hash=API_HASH).start(bot_token=BOT_TOKEN)

user_client = UserClient(StringSession(USER_SESSION_STRING), api_id=API_ID, api_hash=API_HASH)


# The monitored channels and the target channel
monitored_channels = set()
target_channel = "@maxshkilnews"

# A set to store Simhash values of previous messages
simhash_set = set()

# Define the similarity threshold (0 to 64)
similarity_threshold = 10

@client.on(events.NewMessage(pattern="/addchannel"))
async def add_channel(event):
    print(f"Inside add_channel function")
    if event.is_private:
        message_parts = event.raw_text.split(" ")
        if len(message_parts) > 1:
            channel_link = message_parts[1]
            if channel_link.startswith("https://t.me/"):
                channel_username = channel_link[13:]
                try:
                    await user_client(JoinChannelRequest(channel_username))
                    monitored_channels.add(f"@{channel_username}")
                    await event.reply(f"Added {channel_username} to monitored channels.")
                except Exception as e:
                    await event.reply(f"Failed to join the channel. Error: {str(e)}")
            else:
                await event.reply("Please provide a valid Telegram channel link.")
        else:
            await event.reply("Usage: /addchannel https://t.me/channel_username")

def simhash_similarity(simhash1, simhash2):
    distance = bin(simhash1 ^ simhash2).count('1')
    return distance


@user_client.on(events.NewMessage())
async def handle_channel_post(event):
    if event.is_channel and event.chat.username and f"@{event.chat.username}" in monitored_channels:
        message_text = event.text or event.message.text
        if message_text:
            message_simhash = Simhash(message_text).value

            for stored_simhash in simhash_set:
                if simhash_similarity(stored_simhash, message_simhash) <= similarity_threshold:
                    return

            simhash_set.add(message_simhash)

            await event.forward_to(target_channel)




async def main():
    await client.start()
    await user_client.start()
    bot_info = await client.get_me()
    print(f"Successfully connected to the bot @{bot_info.username} ({bot_info.first_name})")

    await client.run_until_disconnected()
    await user_client.run_until_disconnected()

if __name__ == "__main__":
    client.loop.run_until_complete(main())
