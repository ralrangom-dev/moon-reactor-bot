import os
import asyncio
import random

from telegram import Bot, ReactionTypeEmoji


REACTIONS = [
    "🍓",
    "🐳",
    "🌚",
]


# دریافت BOT_TOKEN_1 تا BOT_TOKEN_40
TOKENS = []

for i in range(1, 41):
    token = os.getenv(f"BOT_TOKEN_{i}")

    if token:
        TOKENS.append((i, token))


if not TOKENS:
    raise RuntimeError(
        "هیچ BOT_TOKEN_ای از BOT_TOKEN_1 تا BOT_TOKEN_40 تنظیم نشده است."
    )


async def react_to_message(bot, number, message):
    # انتخاب تصادفی ریکت برای همین پیام
    emoji = random.choice(REACTIONS)

    try:
        await bot.set_message_reaction(
            chat_id=message.chat_id,
            message_id=message.message_id,
            reaction=[
                ReactionTypeEmoji(emoji=emoji)
            ],
        )

        print(
            f"✅ بات {number} | "
            f"پیام {message.message_id} | "
            f"ریکت: {emoji}"
        )

    except Exception as e:
        print(
            f"❌ بات {number} | "
            f"پیام {message.message_id} | "
            f"خطا: {e}"
        )


async def run_bot(number, token):
    bot = Bot(token=token)

    try:
        me = await bot.get_me()

        print(
            f"🟢 بات {number} فعال شد: "
            f"@{me.username or me.id}"
        )

        # حذف Webhook قبلی
        await bot.delete_webhook(
            drop_pending_updates=False
        )

        offset = None

        while True:
            try:
                updates = await bot.get_updates(
                    offset=offset,
                    timeout=30,
                    allowed_updates=["channel_post"],
                )

                for update in updates:

                    offset = update.update_id + 1

                    message = update.channel_post

                    if not message:
                        continue

                    await react_to_message(
                        bot,
                        number,
                        message
                    )

            except Exception as e:

                print(
                    f"⚠️ خطای بات {number}: {e}"
                )

                await asyncio.sleep(5)

    finally:
        await bot.shutdown()


async def main():

    print(
        f"🤖 تعداد بات‌های فعال: {len(TOKENS)}"
    )

    print(
        "🍓 🐳 🌚"
    )

    print(
        "🟢 سیستم ریکت تصادفی فعال شد."
    )

    tasks = []

    for number, token in TOKENS:

        task = asyncio.create_task(
            run_bot(
                number,
                token
            )
        )

        tasks.append(task)

    await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())
