from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from bot.keyboards.support import SUPPORT_PV_URL


def get_test_keyboard(bot_username: str):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(
            "➕ افزودن ربات به گروه",
            url=f"https://t.me/{bot_username}?startgroup=true",
            style="success",
        )],
        [InlineKeyboardButton("☎️ مشاوره و نصب", url=SUPPORT_PV_URL, style="primary")],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="back", style="danger")],
    ])