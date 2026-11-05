from telegram import InlineKeyboardButton, InlineKeyboardMarkup

SUPPORT_PV_URL = "https://t.me/XMrAmer"


def get_support_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📞 پشتیبانی مستقیم", url=SUPPORT_PV_URL)],
        [InlineKeyboardButton("📨 پشتیبانی غیرمستقیم", callback_data="support_ticket")],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="back")],
    ])


def get_ticket_prompt_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 بازگشت", callback_data="support")],
    ])


def get_after_ticket_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🏠 منوی اصلی", callback_data="back")],
    ])