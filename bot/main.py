from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters,
)

from bot.config import TELEGRAM_TOKEN
from bot.database import init_db
from bot.handlers.start import start
from bot.handlers.buttons import button_handler
from bot.handlers.unknown import unknown_message
from bot.handlers.locklink.command import locklink_command
from bot.handlers.locklink.guard import link_guard


def main():
    init_db()
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    # /start فقط توی پیوی
    app.add_handler(CommandHandler("start", start, filters=filters.ChatType.PRIVATE))

    # /locklink فقط توی گروه‌ها
    app.add_handler(CommandHandler("locklink", locklink_command, filters=filters.ChatType.GROUPS))

    # Callback handler (دکمه‌های شیشه‌ای)
    app.add_handler(CallbackQueryHandler(button_handler))

    # پاسخ خودکار پیوی
    app.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND & filters.ChatType.PRIVATE,
        unknown_message
    ))

    # گارد لینک توی گروه‌ها
    app.add_handler(MessageHandler(
        (filters.TEXT | filters.CAPTION) & filters.ChatType.GROUPS,
        link_guard
    ))

    print("Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()