from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from bot.utils.permissions import is_admin_or_owner, BOT_OWNER_ID


# ذخیره وضعیت حالت ویرایشی برای هر گروه
_edit_mode_state = {}


def is_edit_mode_enabled(chat_id: int) -> bool:
    return _edit_mode_state.get(chat_id, False)


def set_edit_mode(chat_id: int, enabled: bool):
    _edit_mode_state[chat_id] = enabled


def get_edit_mode_keyboard(enabled: bool):
    enabled_icon = "🟢" if enabled else "🔴"
    enabled_text = "فعال" if enabled else "غیرفعال"

    keyboard = [
        [InlineKeyboardButton("✏️ حالت ویرایشی فعال", callback_data="editmode_on")],
        [InlineKeyboardButton("🚫 حالت ویرایشی غیرفعال", callback_data="editmode_off")],
        [InlineKeyboardButton(f"{enabled_icon} وضعیت فعلی: {enabled_text}", callback_data="editmode_noop")],
        [InlineKeyboardButton("🔄 بروزرسانی", callback_data="editmode_refresh")],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_edit_mode_text(enabled: bool) -> str:
    status = "🟢 فعال" if enabled else "🔴 غیرفعال"
    return (
        "⚙️ <b>حالت ها</b>\n\n"
        "🔹 حالت ویرایشی، پیام خوش‌آمدگویی ربات رو به‌صورت تدریجی "
        "و با انیمیشن ارسال می‌کنه.\n\n"
        f"وضعیت فعلی: {status}"
    )


async def edit_mode_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    message = update.effective_message

    if chat.type == "private":
        return

    if not await is_admin_or_owner(update, context):
        return

    enabled = is_edit_mode_enabled(chat.id)

    await message.reply_text(
        get_edit_mode_text(enabled),
        parse_mode="HTML",
        reply_markup=get_edit_mode_keyboard(enabled)
    )


async def edit_mode_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data

    if data == "editmode_noop":
        await query.answer()
        return

    user = query.from_user
    chat = query.message.chat

    if user.id != BOT_OWNER_ID:
        try:
            member = await context.bot.get_chat_member(chat.id, user.id)
            if member.status not in ("administrator", "creator"):
                await query.answer("🚫 شما دسترسی ندارید!", show_alert=True)
                return
        except Exception:
            await query.answer("🚫 خطا در بررسی دسترسی!", show_alert=True)
            return

    if data == "editmode_on":
        set_edit_mode(chat.id, True)
        await query.answer("حالت ویرایشی فعال شد!")

    elif data == "editmode_off":
        set_edit_mode(chat.id, False)
        await query.answer("حالت ویرایشی غیرفعال شد!")

    elif data == "editmode_refresh":
        await query.answer("بروزرسانی شد!")

    # به‌روزرسانی پنل
    enabled = is_edit_mode_enabled(chat.id)
    await query.edit_message_text(
        get_edit_mode_text(enabled),
        parse_mode="HTML",
        reply_markup=get_edit_mode_keyboard(enabled)
    )