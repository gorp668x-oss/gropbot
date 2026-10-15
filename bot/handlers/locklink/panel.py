from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from bot.database import get_connection
from bot.utils.permissions import BOT_OWNER_ID


def is_locklink_enabled(chat_id: int) -> bool:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS group_settings (
            chat_id BIGINT PRIMARY KEY,
            lock_link BOOLEAN DEFAULT FALSE
        )
    """)
    cur.execute("SELECT lock_link FROM group_settings WHERE chat_id = %s", (chat_id,))
    row = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    return bool(row and row["lock_link"])


def set_locklink(chat_id: int, enabled: bool):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO group_settings (chat_id, lock_link)
        VALUES (%s, %s)
        ON CONFLICT (chat_id) DO UPDATE SET lock_link = EXCLUDED.lock_link
    """, (chat_id, enabled))
    conn.commit()
    cur.close()
    conn.close()


def get_locklink_keyboard(enabled: bool):
    status = "🟢 روشن" if enabled else "🔴 خاموش"
    action = "🔒 خاموش کردن" if enabled else "🔓 روشن کردن"

    keyboard = [
        [InlineKeyboardButton(action, callback_data="toggle_locklink")],
        [InlineKeyboardButton(f"وضعیت فعلی: {status}", callback_data="noop")],
    ]
    return InlineKeyboardMarkup(keyboard)


def build_panel_text(enabled: bool) -> str:
    return (
        f"🔐 <b>پنل قفل لینک</b>\n\n"
        f"وضعیت فعلی: {'🟢 <b>روشن</b>' if enabled else '🔴 <b>خاموش</b>'}\n\n"
        f"📌 وقتی روشن باشه، هر لینکی که توسط اعضای عادی ارسال بشه، "
        f"حذف شده و به فرستنده هشدار داده می‌شه.\n\n"
        f"👑 ادمین‌ها و سازنده ربات از این قفل مستثنی هستن."
    )


async def locklink_toggle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    chat = query.message.chat
    user = query.from_user

    if user.id != BOT_OWNER_ID:
        try:
            member = await context.bot.get_chat_member(chat.id, user.id)
            if member.status not in ("administrator", "creator"):
                await query.answer("🚫 شما دسترسی ندارید!", show_alert=True)
                return
        except Exception:
            await query.answer("🚫 خطا در بررسی دسترسی!", show_alert=True)
            return

    current = is_locklink_enabled(chat.id)
    new_state = not current
    set_locklink(chat.id, new_state)

    await query.edit_message_text(
        text=build_panel_text(new_state),
        parse_mode="HTML",
        reply_markup=get_locklink_keyboard(new_state)
    )