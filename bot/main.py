from telegram.request import HTTPXRequest
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
from bot.handlers.welcome import (
    welcome_new_member,
    welcome_on_command,
    welcome_off_command,
)
from bot.handlers.panel import panel_command


# Regex خوشامد
WELCOME_ON_PATTERN = (
    r"^خوش[\s‌]*(?:[اآ]?مد(?:گویی|گويي)?)?[\s‌]*(?:روشن|فعال)$"
)
WELCOME_OFF_PATTERN = (
    r"^خوش[\s‌]*(?:[اآ]?مد(?:گویی|گويي)?)?[\s‌]*(?:خاموش|غیر[\s‌]*فعال)$"
)



def main():
    init_db()
    request = HTTPXRequest(connect_timeout=15.0, read_timeout=30.0, pool_timeout=10.0)
    app = Application.builder().token(TELEGRAM_TOKEN).request(request).build()

    # /start فقط در پیوی
    app.add_handler(CommandHandler("start", start, filters=filters.ChatType.PRIVATE))

    # قفل لینک
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

    # خوشامد
    app.add_handler(MessageHandler(
        filters.ChatType.GROUPS & filters.Regex(WELCOME_ON_PATTERN),
        welcome_on_command
    ))
    app.add_handler(MessageHandler(
        filters.ChatType.GROUPS & filters.Regex(WELCOME_OFF_PATTERN),
        welcome_off_command
    ))

    # پنل مدیریت
    app.add_handler(MessageHandler(
        filters.ChatType.GROUPS & filters.Regex(r"^پنل$"),
        panel_command
    ))

    # Callback handler
    app.add_handler(CallbackQueryHandler(button_handler))

    # پاسخ خودکار پیوی
    app.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND & filters.ChatType.PRIVATE,
        unknown_message
    ))

    # گارد لینک
    app.add_handler(MessageHandler(
        (filters.TEXT | filters.CAPTION) & filters.ChatType.GROUPS,
        link_guard
    ), group=1)

    # خوش‌آمدگویی
    app.add_handler(MessageHandler(
        filters.StatusUpdate.NEW_CHAT_MEMBERS & filters.ChatType.GROUPS,
        welcome_new_member
    ), group=2)

    print("Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()