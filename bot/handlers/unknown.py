from telegram import Update, LinkPreviewOptions
from telegram.ext import ContextTypes

from bot.texts.unknown import UNKNOWN_REPLY


async def unknown_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        UNKNOWN_REPLY,
        link_preview_options=LinkPreviewOptions(is_disabled=True)
    )