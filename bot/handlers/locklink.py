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
        return

    # اگه کاربر مجاز نیست، هیچ واکنشی نشون نده
    if not await is_admin_or_owner(update, context):
        return

    # اگه از قبل فعال بود
    if is_locklink_enabled(chat.id):
        await message.reply_text("⋅• قفل لینک در حال حاضر فعال است !")
        return

    set_locklink(chat.id, True)
    await message.reply_text("⋅• قفل لینک با موفقیت فعال شد !")


async def unlock_link_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    message = update.effective_message

    if chat.type == "private":
        return

    # اگه کاربر مجاز نیست، هیچ واکنشی نشون نده
    if not await is_admin_or_owner(update, context):
        return

    # اگه از قبل غیرفعال بود
    if not is_locklink_enabled(chat.id):
        await message.reply_text("•⋅ قفل لینک در حال حاضر غیرفعال است !")
        return

    set_locklink(chat.id, False)
    await message.reply_text("•⋅ قفل لینک با موفقیت غیرفعال شد !")