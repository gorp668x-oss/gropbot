from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from bot.texts.panel import (
    PANEL_TEXT,
    PANEL_SOON_TOAST,
    PANEL_NOT_YOURS,
    PANEL_CLOSED_TEXT,
)
from bot.utils.permissions import is_admin_or_owner


def get_panel_keyboard(user_id: int):
    def cb(action: str) -> str:
        return f"panel:{user_id}:{action}"

    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🔒 قفل‌ها", callback_data=cb("locks"), style="primary"),
            InlineKeyboardButton("📋 لیست‌ها", callback_data=cb("lists"), style="primary"),
        ],
        [
            InlineKeyboardButton("⚙️ تنظیمات پیشرفته", callback_data=cb("advanced"), style="primary"),
            InlineKeyboardButton("📖 راهنما", callback_data=cb("guide"), style="success"),
        ],
        [InlineKeyboardButton("✖️ بستن پنل", callback_data=cb("close"), style="danger")],
    ])


async def panel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    message = update.effective_message
    user = update.effective_user
    if chat is None or message is None or user is None or chat.type == "private":
        return

    # فقط مالک گروه، ادمین‌ها و سازنده ربات؛ برای بقیه هیچ واکنشی نیست
    if not await is_admin_or_owner(update, context):
        return

    await message.reply_text(
        PANEL_TEXT,
        parse_mode=ParseMode.HTML,
        reply_markup=get_panel_keyboard(user.id),
    )


async def panel_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    try:
        _, opener, action = query.data.split(":", 2)
        opener_id = int(opener)
    except Exception:
        await query.answer()
        return

    # فقط همان کسی که پنل را باز کرده می‌تواند از آن استفاده کند
    if query.from_user.id != opener_id:
        await query.answer(PANEL_NOT_YOURS, show_alert=True)
        return

    if action == "close":
        await query.answer()
        try:
            await query.edit_message_text(PANEL_CLOSED_TEXT)
        except Exception:
            pass
        return

    await query.answer(PANEL_SOON_TOAST, show_alert=True)