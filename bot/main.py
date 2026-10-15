from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters,
)

from bot.config import TELEGRAM_TOKEN
from bot.database import init_db
from bot.handlers.start import start
from bot.handlers.buttons import button_handler
from bot.handlers.unknown import unknown_message
from bot.handlers.locklink import lock_link_command, unlock_link_command
from bot.handlers.link_guard import link_guard


def main():
    init_db()
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    # /start فقط در پیوی
    app.add_handler(CommandHandler("start", start, filters=filters.ChatType.PRIVATE))

    # دستورات فارسی قفل لینک
    app.add_handler(MessageHandler(
        filters.ChatType.GROUPS & filters.Regex(r"^قفل\s*لینک$"),
        lock_link_command
    ))
    app.add_handler(MessageHandler(
        filters.ChatType.GROUPS & filters.Regex(r"^باز\s*کردن\s*قفل\s*لینک$"),
        unlock_link_command
    ))
    app.add_handler(MessageHandler(
        filters.ChatType.GROUPS & filters.Regex(r"^باز\s*کردن\s*لینک$"),
        unlock_link_command
    ))
    app.add_handler(MessageHandler(
        filters.ChatType.GROUPS & filters.Regex(r"^بازکردن\s*لینک$"),
        unlock_link_command
    ))

    # Callback handler
    app.add_handler(CallbackQueryHandler(button_handler))

    # پاسخ خودکار پیوی
    app.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND & filters.ChatType.PRIVATE,
        unknown_message
    ))

    # گارد لینک در گروه‌ها (group=1 تا با دستورات فارسی تداخل نکنه)
    app.add_handler(MessageHandler(
        (filters.TEXT | filters.CAPTION) & filters.ChatType.GROUPS,
        link_guard
    ), group=1)

    print("Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()