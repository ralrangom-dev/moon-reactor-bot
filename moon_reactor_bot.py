import os
import asyncio
from telegram import Bot
from telegram.error import TelegramError

REACTION = "🌚"

TOKENS = [
    os.getenv(f"BOT_TOKEN_{i}")
    for i in range(1, 41)
]

TOKENS = [token for token in TOKENS if token]

if not TOKENS:
    raise RuntimeError("هیچ BOT_TOKEN_ای تنظیم نشده است.")


async def react_with_bot(token, chat_id, message_id, number):
    try:
        bot = Bot(token)

        await bot.set_message_reaction(
            chat_id=chat_id,
            message_id=message_id,
            reaction=[{
                "type": "emoji",
                "emoji": REACTION
            }]
        )

        print(f"🌚 بات {number}: پیام {message_id}")

        await bot.shutdown()

    except TelegramError as e:
        print(f"❌ بات {number}: {e}")

    except Exception as e:
        print(f"❌ بات {number}: {e}")


async def process_post(chat_id, message_id):
    tasks = []

    for number, token in enumerate(TOKENS, start=1):
        tasks.append(
            react_with_bot(
                token,
                chat_id,
                message_id,
                number
            )
        )

    await asyncio.gather(*tasks)


async def main():
    print(f"🟢 تعداد بات‌های فعال: {len(TOKENS)}")
    print("🌚 سیستم ریکت فعال است.")

    # این قسمت باید با دریافت پست جدید اجرا شود.
    # فعلاً برای تست ساختار چندباتی آماده شده است.


if __name__ == "__main__":
    asyncio.run(main())
