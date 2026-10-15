from telegram import Update
from telegram.ext import ContextTypes

from bot.texts.welcome import WELCOME_TEXT
from bot.texts.about import ABOUT_TEXT
from bot.texts.more_info import MORE_INFO_TEXT
from bot.texts.diff import DIFF_TEXT
from bot.keyboards.main_menu import get_main_keyboard
from bot.keyboards.back import get_back_keyboard
from bot.handlers.locklink.panel import locklink_toggle


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    if query.data == "noop":
        await query.answer()
        return

    if query.data == "toggle_locklink":
        await locklink_toggle(update, context)
        return

    await query.answer()

    if query.data == "about":
        await query.edit_message_text(
            text=ABOUT_TEXT,
            parse_mode="HTML",
            reply_markup=get_back_keyboard()
        )
    elif query.data == "more_info":
        await query.edit_message_text(
            text=MORE_INFO_TEXT,
            parse_mode="HTML",
            reply_markup=get_back_keyboard()
        )
    elif query.data == "diff":
        await query.edit_message_text(
            text=DIFF_TEXT,
            parse_mode="HTML",
            reply_markup=get_back_keyboard()
        )
    elif query.data == "back":
        user = query.from_user
        mention = f'<a href="tg://user?id={user.id}">𓄂꯭ꪰᴀ꯭ᷧᴍ꯭ⷨᴇ꯭ⷷʀ꯭ᷢ↬𓃮™</a>'
        await query.edit_message_text(
            text=WELCOME_TEXT.format(mention=mention),
            parse_mode="HTML",
            reply_markup=get_main_keyboard()
        )