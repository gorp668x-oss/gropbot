from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def get_back_keyboard():
    keyboard = [
        [InlineKeyboardButton("🔙 بازگشت", callback_data="back")]
    ]
    return InlineKeyboardMarkup(keyboard)