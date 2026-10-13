import os
import asyncio
import random
import logging

from telegram import Bot, ReactionTypeEmoji
from telegram.error import (
    Conflict,
    RetryAfter,
    TelegramError,
)

REACTIONS = ["🍓", "🌚"]

POLL_TIMEOUT = 20
RETRY_DELAY = 5

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger("moon-reactor")

TOKENS = []
USED_TOKENS = set()

for i in range(1, 41):
    token = os.getenv(f"BOT_TOKEN_{i}", "").strip()

    if not token:
        continue

    if token in USED_TOKENS:
        logger.error("بات %s: توکن تکراری است.", i)
        continue

    USED_TOKENS.add(token)
    TOKENS.append((i, token))

if not TOKENS:
    raise RuntimeError("هیچ توکنی تنظیم نشده است.")


async def react_to_message(bot, number, message):
    emoji = random.choice(REACTIONS)

    try:
        await bot.set_message_reaction(
            chat_id=message.chat_id,
            message_id=message.message_id,
            reaction=[
                ReactionTypeEmoji(emoji=emoji)
            ],
        )

        logger.info(
            "✅ بات %s | پیام %s | ریکت %s",
            number,
            message.message_id,
            emoji,
        )

    except RetryAfter as e:
        logger.warning(
            "بات %s: محدودیت درخواست؛ %s ثانیه",
            number,
            e.retry_after,
        )
        await asyncio.sleep(float(e.retry_after))

    except TelegramError as e:
        logger.error(
            "❌ بات %s | پیام %s | خطا: %s",
            number,
            message.message_id,
            e,
        )

    except Exception:
        logger.exception(
            "خطای نامشخص بات %s",
            number,
        )


async def run_bot(number, token):
    bot = Bot(token=token)

    try:
        me = await bot.get_me()

        logger.info(
            "🟢 بات %s فعال شد: @%s",
            number,
            me.username or me.id,
        )

        await bot.delete_webhook(
            drop_pending_updates=False
        )

        offset = None

        while True:
            try:
                updates = await bot.get_updates(
                    offset=offset,
                    timeout=POLL_TIMEOUT,
                    allowed_updates=["channel_post"],
                )

                for update in updates:
                    offset = update.update_id + 1

                    message = update.channel_post

                    if message is None:
                        continue

                    await react_to_message(
                        bot,
                        number,
                        message,
                    )

            except Conflict as e:
                logger.error(
                    "⚠️ بات %s | تداخل دریافت پیام: %s",
                    number,
                    e,
                )

                # این خطا با مکث به‌تنهایی رفع نمی‌شود.
                await asyncio.sleep(15)

            except RetryAfter as e:
                await asyncio.sleep(float(e.retry_after))

            except TelegramError as e:
                logger.error(
                    "بات %s | خطای تلگرام: %s",
                    number,
                    e,
                )
                await asyncio.sleep(RETRY_DELAY)

            except asyncio.CancelledError:
                raise

            except Exception:
                logger.exception(
                    "بات %s | خطای پیش‌بینی‌نشده",
                    number,
                )
                await asyncio.sleep(RETRY_DELAY)

    finally:
        await bot.shutdown()


async def main():
    logger.info("تعداد بات‌های تنظیم‌شده: %s", len(TOKENS))

    tasks = [
        asyncio.create_task(run_bot(number, token))
        for number, token in TOKENS
    ]

    try:
        await asyncio.gather(*tasks)
    finally:
        for task in tasks:
            task.cancel()

        await asyncio.gather(
            *tasks,
            return_exceptions=True,
        )


if __name__ == "__main__":
    asyncio.run(main())
