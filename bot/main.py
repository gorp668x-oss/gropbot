from telegram.request import HTTPXRequest
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters,
)

from bot.config import TELEGRAM_TOKEN
from bot.database import init_db
from bot.handlers.start import start
from bot.handlers.buttons import button_handler
from bot.handlers.support import support_callback, ticket_message_handler
from bot.handlers.unknown import unknown_message
from bot.handlers.owner import install_command, uninstall_command, leave_command
from bot.handlers.panel import panel_command, panel_callback

INSTALL_PATTERN = r"^\+\s*نصب$"
UNINSTALL_PATTERN = r"^[-–—−]\s*نصب$"
LEAVE_PATTERN = r"^خروج$"
PANEL_PATTERN = r"^پنل$"


def main():
    init_db()
    request = HTTPXRequest(connect_timeout=15.0, read_timeout=30.0, pool_timeout=10.0)
    app = Application.builder().token(TELEGRAM_TOKEN).request(request).build()

    # /start فقط در پیوی
    app.add_handler(CommandHandler("start", start, filters=filters.ChatType.PRIVATE))

    # دستورات گروه: نصب / حذف نصب / خروج (فقط سازنده ربات) و پنل (ادمین‌ها)
    app.add_handler(MessageHandler(filters.ChatType.GROUPS & filters.Regex(INSTALL_PATTERN), install_command))
    app.add_handler(MessageHandler(filters.ChatType.GROUPS & filters.Regex(UNINSTALL_PATTERN), uninstall_command))
    app.add_handler(MessageHandler(filters.ChatType.GROUPS & filters.Regex(LEAVE_PATTERN), leave_command))
    app.add_handler(MessageHandler(filters.ChatType.GROUPS & filters.Regex(PANEL_PATTERN), panel_command))

    # دکمه‌ها (موارد اختصاصی قبل از هندلر عمومی)
    app.add_handler(CallbackQueryHandler(panel_callback, pattern=r"^panel:"))
    app.add_handler(CallbackQueryHandler(support_callback, pattern=r"^support(_ticket)?$"))
    app.add_handler(CallbackQueryHandler(button_handler))

    # پشتیبانی غیرمستقیم / پاسخ سازنده (قبل از پاسخ خودکار پیوی)
    app.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND & filters.ChatType.PRIVATE,
        ticket_message_handler
    ), group=-1)

    # پاسخ خودکار پیوی
    app.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND & filters.ChatType.PRIVATE,
        unknown_message
    ))

    print("Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()