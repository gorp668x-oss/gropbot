from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def get_main_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("📢 کانال ربات", url="https://t.me/BOTXTMBOT"),
            InlineKeyboardButton("💬 گروه پشتیبانی", url="https://t.me/GPBOTXTMBOT"),
        ],
        [
            InlineKeyboardButton("👨‍💻 پشتیبانی", url="https://t.me/XMrAmer"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)
