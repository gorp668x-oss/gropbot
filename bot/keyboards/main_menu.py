from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def get_main_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("📓 اطلاعات بیشتر", callback_data="more_info", style="primary"),
        ],
        [
            InlineKeyboardButton("📢 کانال ربات", url="https://t.me/BOTXTMBOT"),
            InlineKeyboardButton("💬 گروه پشتیبانی", url="https://t.me/GPBOTXTMBOT"),
        ],
        [
            InlineKeyboardButton("🆚 تفاوت ربات رایگان با اشتراکی", callback_data="diff", style="success"),
        ],
        [
            InlineKeyboardButton("👨‍💻 پشتیبانی", url="https://t.me/XMrAmer"),
            InlineKeyboardButton("ℹ️ درباره ما", callback_data="about"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)