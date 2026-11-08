from telegram.request import HTTPXRequest
from telegram.ext import Application, CommandHandler, MessageHandler, filters

from bot.config import TELEGRAM_TOKEN
from bot.database import init_db
from bot.handlers.start import start
from bot.handlers.unknown import unknown_message


def main():
    init_db()
    request = HTTPXRequest(connect_timeout=15.0, read_timeout=30.0, pool_timeout=10.0)
    app = Application.builder().token(TELEGRAM_TOKEN).request(request).build()

    # فقط دستور استارت در پیوی
    app.add_handler(CommandHandler("start", start, filters=filters.ChatType.PRIVATE))

    # پاسخ خودکار به پیام‌های ناشناس در پیوی
    app.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND & filters.ChatType.PRIVATE,
        unknown_message,
    ))

    print("Bot is running (only /start)...")
    app.run_polling()


if __name__ == "__main__":
    main()
