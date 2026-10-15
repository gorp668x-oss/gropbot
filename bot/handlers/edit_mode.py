import asyncio

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
        [InlineKeyboardButton("🎬 حالت انتخاب", callback_data="editmode_noop")],
        [InlineKeyboardButton(f"✏️ حالت ویرایشی فعال", callback_data="editmode_on")],
        [InlineKeyboardButton(f"🚫 حالت ویرایشی غیرفعال", callback_data="editmode_off")],
        [InlineKeyboardButton(f"{enabled_icon} وضعیت فعلی: {enabled_text}", callback_data="editmode_noop")],
        [InlineKeyboardButton("🔄 بروزرسانی", callback_data="editmode_refresh")],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_edit_mode_text(enabled: bool) -> str:
    status = "🟢 فعال" if enabled else "🔴 غیرفعال"
    return (
        "⚙️ <b>حالت ها</b>\n\n"
        "🔹 حالت ویرایشی به شما این امکان رو می‌ده که پیام‌های ربات به‌صورت "
        "تدریجی و با انیمیشن ویرایش بشن.\n\n"
        "📌 از دکمه‌های زیر، حالت موردنظر خودتون رو انتخاب کنید.\n\n"
        f"وضعیت فعلی: {status}"
    )


async def edit_mode_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """دستور: حالت ها"""
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


async def _type_animation(query, target_text: str, delay: float = 0.35):
    """انیمیشن تایپ: س → سل → سلا → سلام"""
    # پیام اول رو با یه نقطه شروع کن
    if not target_text:
        return

    for i in range(1, len(target_text) + 1):
        partial = target_text[:i]
        try:
            await query.edit_message_text(
                text=partial,
                reply_markup=None
            )
        except Exception:
            # اگه پیام عوض نشد، بی‌خیال
            pass
        await asyncio.sleep(delay)


async def edit_mode_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data

    if data == "editmode_noop":
        await query.answer()
        return

    user = query.from_user
    chat = query.message.chat

    # چک دسترسی
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

        # انیمیشن تایپ
        await _type_animation(query, "سلام")

        await asyncio.sleep(0.5)

        # برگشت به پنل با وضعیت جدید
        await query.edit_message_text(
            get_edit_mode_text(True),
            parse_mode="HTML",
            reply_markup=get_edit_mode_keyboard(True)
        )

    elif data == "editmode_off":
        set_edit_mode(chat.id, False)
        await query.answer("حالت ویرایشی غیرفعال شد!")

        # انیمیشن معکوس یا پیام ساده
        await query.edit_message_text("حالت ویرایشی غیرفعال شد.")
        await asyncio.sleep(0.8)

        await query.edit_message_text(
            get_edit_mode_text(False),
            parse_mode="HTML",
            reply_markup=get_edit_mode_keyboard(False)
        )

    elif data == "editmode_refresh":
        enabled = is_edit_mode_enabled(chat.id)
        await query.answer("بروزرسانی شد!")
        await query.edit_message_text(
            get_edit_mode_text(enabled),
            parse_mode="HTML",
            reply_markup=get_edit_mode_keyboard(enabled)
        )