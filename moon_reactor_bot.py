import os
import asyncio
import random
import logging

from telegram import Bot, ReactionTypeEmoji
from telegram.error import Conflict, RetryAfter, TelegramError


REACTIONS = ["🍓", "🌚"]

POLL_TIMEOUT = 25
RETRY_DELAY = 5
CONFLICT_DELAY = 30

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger("moon-reactor")

# خواندن توکن‌ها
TOKENS = []
SEEN_TOKENS = set()

for i in range(1, 41):
    token = os.getenv(f"BOT_TOKEN_{i}", "").strip()

    if not token:
        continue

    # جلوگیری از اجرای یک توکن تکراری در همین برنامه
    if token in SEEN_TOKENS:
        logger.error(
            "توکن تکراری است؛ بات شماره %s اجرا نمی‌شود.", i
        )
        continue

    SEEN_TOKENS.add(token)
    TOKENS.append((i, token))

if not TOKENS:
    raise RuntimeError(
        "هیچ توکن معتبری در BOT_TOKEN_1 تا BOT_TOKEN_40 پیدا نشد."
    )


async def react_to_message(bot, number, message):
    emoji = random.choice(REACTIONS)

    try:
        await bot.set_message_reaction(
            chat_id=message.chat_id,
            message_id=message.message_id,
            reaction=[ReactionTypeEmoji(emoji=emoji)],
        )

        logger.info(
            "بات %s | پیام %s | ریکت %s",
            number, message.message_id, emoji,
        )
        return True

    except RetryAfter as e:
        logger.warning(
            "بات %s | محدودیت درخواست؛ %s ثانیه صبر",
            number, e.retry_after,
        )
        await asyncio.sleep(float(e.retry_after))
        return False

    except TelegramError as e:
        logger.error(
            "بات %s | پیام %s | خطای ریکت: %s",
            number, message.message_id, e,
        )
        return False


async def run_bot(number, token):
    bot = Bot(token=token)

    try:
        me = await bot.get_me()
        logger.info(
            "بات %s فعال شد: @%s",
            number, me.username or me.id,
        )

        # پاک کردن webhook برای استفاده از polling
        await bot.delete_webhook(drop_pending_updates=False)

        offset = None

        while True:
            try:
                updates = await bot.get_updates(
                    offset=offset,
                    timeout=POLL_TIMEOUT,
                    allowed_updates=["channel_post"],
                )

                for update in updates:
                    # به‌روزرسانی offset حتی برای پیام‌های نادیده‌گرفته‌شده
                    offset = update.update_id + 1

                    message = update.channel_post
                    if message is None:
                        continue

                    await react_to_message(bot, number, message)

            except Conflict as e:
                logger.error(
                    "بات %s | تداخل getUpdates: %s",
                    number, e,
                )
                # اگر نمونه دیگری فعال باشد، این مکث مشکل را
                # به‌تنهایی حل نمی‌کند؛ از حلقه سریع خطا جلوگیری می‌کند.
                await asyncio.sleep(CONFLICT_DELAY)

            except RetryAfter as e:
                await asyncio.sleep(float(e.retry_after))

            except TelegramError as e:
                logger.error("بات %s | خطای تلگرام: %s", number, e)
                await asyncio.sleep(RETRY_DELAY)

            except asyncio.CancelledError:
                raise

            except Exception:
                logger.exception("بات %s | خطای پیش‌بینی‌نشده", number)
                await asyncio.sleep(RETRY_DELAY)

    finally:
        await bot.shutdown()


async def main():
    logger.info("تعداد بات‌ها: %s", len(TOKENS))

    tasks = [
        asyncio.create_task(run_bot(number, token))
        for number, token in TOKENS
    ]

    try:
        await asyncio.gather(*tasks)
    finally:
        for task in tasks:
            task.cancel()

        await asyncio.gather(*tasks, return_exceptions=True)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("برنامه متوقف شد.")
