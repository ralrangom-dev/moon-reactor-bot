import os
import asyncio
from telethon import TelegramClient, events, functions, types

API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "")
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
CHANNEL = os.getenv("CHANNEL", "")
REACTION = "🌚"

if not API_ID or not API_HASH or not BOT_TOKEN or not CHANNEL:
    raise RuntimeError("API_ID, API_HASH, BOT_TOKEN و CHANNEL را تنظیم کنید.")

client = TelegramClient("moon_reactor_session", API_ID, API_HASH)


async def react_to_message(message):
    try:
        await client(
            functions.messages.SendReactionRequest(
                peer=CHANNEL,
                msg_id=message.id,
                reaction=[types.ReactionEmoji(emoticon=REACTION)],
                big=False,
                add_to_recent=False,
            )
        )
        print(f"🌚 پیام {message.id} انجام شد")
    except Exception as e:
        print(f"❌ پیام {message.id}: {e}")


async def react_to_old_messages():
    print("🔎 شروع بررسی پیام‌های قبلی...")
    count = 0

    async for message in client.iter_messages(CHANNEL, reverse=True):
        if message and not message.out:
            await react_to_message(message)
            count += 1
            await asyncio.sleep(0.15)

    print(f"✅ بررسی پیام‌های قبلی تمام شد: {count} پیام")


@client.on(events.NewMessage(chats=CHANNEL))
async def new_channel_message(event):
    await react_to_message(event.message)


async def main():
    await client.start(bot_token=BOT_TOKEN)

    me = await client.get_me()
    print(f"🤖 ربات فعال شد: @{me.username or me.id}")
    print(f"📢 کانال: {CHANNEL}")
    print("🌚 واکنش: 🌚")

    await react_to_old_messages()

    print("🟢 از این لحظه پیام‌های جدید هم خودکار 🌚 می‌گیرند.")
    await client.run_until_disconnected()


if __name__ == "__main__":
    asyncio.run(main())
