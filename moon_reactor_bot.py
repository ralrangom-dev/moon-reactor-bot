import os
from telegram import Update, ReactionTypeEmoji
from telegram.ext import Application, ChannelPostHandler, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")
REACTION = "🌚"

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN تنظیم نشده است.")

async def react_to_new_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.channel_post
    if not message:
        return
    try:
        await context.bot.set_message_reaction(
            chat_id=message.chat_id,
            message_id=message.message_id,
            reaction=[ReactionTypeEmoji(emoji=REACTION)],
        )
        print(f"🌚 پیام {message.message_id}")
    except Exception as e:
        print(f"❌ پیام {message.message_id}: {e}")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(ChannelPostHandler(react_to_new_post))
    print("🟢 ربات فعال شد؛ پست‌های جدید کانال خودکار 🌚 می‌گیرند.")
    app.run_polling(allowed_updates=["channel_post"])

if __name__ == "__main__":
    main()
