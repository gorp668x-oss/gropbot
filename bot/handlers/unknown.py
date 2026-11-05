from telegram import Update, LinkPreviewOptions
from telegram.ext import ContextTypes

from bot.texts.unknown import UNKNOWN_REPLY
from bot.utils.stream import stream_draft


async def unknown_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await stream_draft(
        context.bot.token, update.effective_chat.id, UNKNOWN_REPLY,
        delay=0.12, max_steps=10,
    )
    await update.message.reply_text(
        UNKNOWN_REPLY,
        link_preview_options=LinkPreviewOptions(is_disabled=True),
    )