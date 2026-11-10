from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def get_main_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("🧩 امکانات ربات", callback_data="features", style="success"),
            InlineKeyboardButton("🚦 راهنمای تست", callback_data="test_guide", style="success"),
        ],
        [
            InlineKeyboardButton("📓 اطلاعات بیشتر", callback_data="more_info", style="primary"),
        ],
        [
            InlineKeyboardButton("📢 کانال ربات", url="https://t.me/BOTXTMBOT", style="success"),
            InlineKeyboardButton("💬 گروه پشتیبانی", url="https://t.me/GPBOTXTMBOT", style="success"),
        ],
        [
            InlineKeyboardButton("🆚 تفاوت ربات رایگان با اشتراکی", callback_data="diff", style="primary"),
        ],
        [
            InlineKeyboardButton("👨‍💻 پشتیبانی", callback_data="support", style="primary"),
            InlineKeyboardButton("ℹ️ درباره تیم", callback_data="about", style="primary"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)