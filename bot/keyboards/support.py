from telegram import InlineKeyboardButton, InlineKeyboardMarkup

SUPPORT_PV_URL = "https://t.me/XMrAmer"


def get_support_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("☎️ پشتیبانی مستقیم", url=SUPPORT_PV_URL, style="success")],
        [InlineKeyboardButton("📬 پشتیبانی غیرمستقیم", callback_data="support_ticket", style="primary")],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="back", style="danger")],
    ])


def get_ticket_prompt_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 بازگشت", callback_data="support", style="danger")],
    ])


def get_after_ticket_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🏠 منوی اصلی", callback_data="back", style="primary")],
    ])