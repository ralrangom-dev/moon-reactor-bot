import os
import asyncio
from telegram import Bot, ReactionTypeEmoji


REACTION = "🌚"


# گرفتن توکن‌های BOT_TOKEN_1 تا BOT_TOKEN_40
TOKENS = []

for i in range(1, 41):
    token = os.getenv(f"BOT_TOKEN_{i}")
    if token:
        TOKENS.append((i, token))


if not TOKENS:
    raise RuntimeError(
        "هیچ متغیر BOT_TOKEN_1 تا BOT_TOKEN_40 تنظیم نشده است."
    )


async def run_bot(number, token):
    bot = Bot(token=token)

    try:
        me = await bot.get_me()
        print(f"🟢 بات {number} فعال شد: @{me.username}")

        # حذف webhook قبلی تا polling کار کند
        await bot.delete_webhook(drop_pending_updates=False)

        offset = None

        while True:
            try:
                updates = await bot.get_updates(
                    offset=offset,
                    timeout=30,
                    allowed_updates=["channel_post"]
                )

                for update in updates:
                    offset = update.update_id + 1

                    message = update.channel_post

                    if not message:
                        continue

                    try:
                        await bot.set_message_reaction(
                            chat_id=message.chat_id,
                            message_id=message.message_id,
                            reaction=[
                                ReactionTypeEmoji(emoji=REACTION)
                            ]
                        )

                        print(
                            f"🌚 بات {number} "
                            f"روی پیام {message.message_id} ریکت زد"
                        )

                    except Exception as e:
                        print(
                            f"❌ بات {number} "
                            f"خطای ریکت: {e}"
                        )

            except Exception as e:
                print(f"⚠️ بات {number}: {e}")
                await asyncio.sleep(5)

    finally:
        await bot.shutdown()


async def main():
    print(f"🤖 تعداد بات‌ها: {len(TOKENS)}")
    print("🌚 سیستم ریکت فعال شد.")

    tasks = []

    for number, token in TOKENS:
        tasks.append(
            asyncio.create_task(
                run_bot(number, token)
            )
        )

    await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())
