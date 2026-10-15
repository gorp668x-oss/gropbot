from telegram import Update
from telegram.ext import ContextTypes

from bot.utils.permissions import is_admin_or_owner
from bot.handlers.locklink.panel import (
    is_locklink_enabled,
    get_locklink_keyboard,
    build_panel_text,
)


async def locklink_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat

    if chat.type == "private":
        await update.message.reply_text(
            "⚠️ این دستور فقط توی گروه‌ها قابل استفاده است."
        )
        return

    if not await is_admin_or_owner(update, context):
        await update.message.reply_text(
            "🚫 <b>دسترسی رد شد</b>\n\n"
            "این دستور فقط برای <b>مالک گروه، ادمین‌ها و سازنده ربات</b> قابل استفاده است.",
            parse_mode="HTML"
        )
        return

    enabled = is_locklink_enabled(chat.id)

    await update.message.reply_html(
        build_panel_text(enabled),
        reply_markup=get_locklink_keyboard(enabled)
    )