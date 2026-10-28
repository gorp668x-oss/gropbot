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
from bot.handlers.locks import (
    lock_gif, unlock_gif, lock_sticker, unlock_sticker,
    lock_photo, unlock_photo, lock_video, unlock_video,
    lock_video_note, unlock_video_note, lock_media, unlock_media,
    media_guard
)


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


    # قفل رسانه ها
    app.add_handler(MessageHandler(filters.ChatType.GROUPS & filters.Regex(r"^قفل گیف$"), lock_gif))
    app.add_handler(MessageHandler(filters.ChatType.GROUPS & filters.Regex(r"^باز کردن گیف$|^بازکردن گیف$"), unlock_gif))
    
    app.add_handler(MessageHandler(filters.ChatType.GROUPS & filters.Regex(r"^قفل استیکر$"), lock_sticker))
    app.add_handler(MessageHandler(filters.ChatType.GROUPS & filters.Regex(r"^باز کردن استیکر$|^بازکردن استیکر$"), unlock_sticker))
    
    app.add_handler(MessageHandler(filters.ChatType.GROUPS & filters.Regex(r"^قفل عکس$"), lock_photo))
    app.add_handler(MessageHandler(filters.ChatType.GROUPS & filters.Regex(r"^باز کردن عکس$|^بازکردن عکس$"), unlock_photo))
    
    app.add_handler(MessageHandler(filters.ChatType.GROUPS & filters.Regex(r"^قفل فیلم$"), lock_video))
    app.add_handler(MessageHandler(filters.ChatType.GROUPS & filters.Regex(r"^باز کردن فیلم$|^بازکردن فیلم$"), unlock_video))
    
    app.add_handler(MessageHandler(filters.ChatType.GROUPS & filters.Regex(r"^قفل ویدیو مسیج$"), lock_video_note))
    app.add_handler(MessageHandler(filters.ChatType.GROUPS & filters.Regex(r"^باز کردن ویدیو مسیج$|^بازکردن ویدیو مسیج$"), unlock_video_note))
    
    app.add_handler(MessageHandler(filters.ChatType.GROUPS & filters.Regex(r"^قفل رسانه$"), lock_media))
    app.add_handler(MessageHandler(filters.ChatType.GROUPS & filters.Regex(r"^باز کردن رسانه$|^بازکردن رسانه$"), unlock_media))

    # گارد رسانه ها
    app.add_handler(MessageHandler(
        (filters.ANIMATION | filters.Sticker.ALL | filters.PHOTO | filters.VIDEO | filters.VIDEO_NOTE | filters.Document.ALL | filters.VOICE | filters.AUDIO) & filters.ChatType.GROUPS,
        media_guard
    ), group=3)

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