from telegram import Update
from telegram.ext import ContextTypes

from bot.database import get_connection
from bot.utils.permissions import is_admin_or_owner


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


async def lock_link_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    message = update.effective_message

    if chat.type == "private":
        await message.reply_text("⚠️ این دستور تنها در گروه‌ها قابل استفاده است.")
        return

    if not await is_admin_or_owner(update, context):
        await message.reply_text(
            "🚫 <b>دسترسی رد شد</b>\n\n"
            "این دستور تنها برای <b>مالک گروه، ادمین‌ها و سازنده ربات</b> قابل استفاده است.",
            parse_mode="HTML"
        )
        return

    set_locklink(chat.id, True)

    await message.reply_text(
        "🔒 <b>قفل لینک با موفقیت فعال شد.</b>\n\n"
        "از این پس، ارسال هرگونه لینک توسط اعضای عادی در گروه ممنوع بوده و "
        "پیام ارسال‌کننده حذف خواهد شد.\n\n"
        "👑 ادمین‌ها و سازنده ربات از این محدودیت مستثنی هستند.",
        parse_mode="HTML"
    )


async def unlock_link_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    message = update.effective_message

    if chat.type == "private":
        await message.reply_text("⚠️ این دستور تنها در گروه‌ها قابل استفاده است.")
        return

    if not await is_admin_or_owner(update, context):
        await message.reply_text(
            "🚫 <b>دسترسی رد شد</b>\n\n"
            "این دستور تنها برای <b>مالک گروه، ادمین‌ها و سازنده ربات</b> قابل استفاده است.",
            parse_mode="HTML"
        )
        return

    set_locklink(chat.id, False)

    await message.reply_text(
        "🔓 <b>قفل لینک با موفقیت غیرفعال شد.</b>\n\n"
        "از این پس، اعضای گروه می‌توانند بدون محدودیت لینک ارسال کنند.",
        parse_mode="HTML"
    )