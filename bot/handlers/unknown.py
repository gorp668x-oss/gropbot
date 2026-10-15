from telegram import Update
from telegram.ext import ContextTypes

from bot.texts.unknown import UNKNOWN_REPLY


async def unknown_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        UNKNOWN_REPLY,
        disable_web_page_preview=True
    )