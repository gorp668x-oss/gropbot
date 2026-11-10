import html

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from bot.database import get_connection
from bot.texts.owner import (
    INSTALL_OK_TEXT,
    INSTALL_EXISTS_TEXT,
    UNINSTALL_OK_TEXT,
    UNINSTALL_MISSING_TEXT,
    LEAVE_TEXT,
    DB_ERROR_TEXT,
    LEAVE_FAILED_TEXT,
)
from bot.utils.permissions import BOT_OWNER_ID

_table_ready = False


# ───────────────────────── دیتابیس ─────────────────────────
def _ensure_table():
    global _table_ready
    if _table_ready:
        return
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS installed_groups (
            chat_id BIGINT PRIMARY KEY,
            title TEXT,
            installed_by BIGINT,
            installed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    cur.close()
    conn.close()
    _table_ready = True


def _add_group(chat_id, title, user_id) -> bool:
    """True اگر گروه تازه ثبت شد؛ False اگر از قبل ثبت بود."""
    _ensure_table()
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """INSERT INTO installed_groups (chat_id, title, installed_by)
           VALUES (%s, %s, %s)
           ON CONFLICT (chat_id) DO NOTHING
           RETURNING chat_id""",
        (chat_id, title, user_id),
    )
    row = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    return row is not None


def _remove_group(chat_id) -> bool:
    """True اگر گروه در لیست بود و حذف شد."""
    _ensure_table()
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "DELETE FROM installed_groups WHERE chat_id = %s RETURNING chat_id",
        (chat_id,),
    )
    row = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    return row is not None


def _presence_seconds(chat_id):
    """چند ثانیه از ثبت گروه گذشته؛ None اگر گروه در لیست نیست."""
    _ensure_table()
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """SELECT EXTRACT(EPOCH FROM (CURRENT_TIMESTAMP - installed_at)) AS s
           FROM installed_groups WHERE chat_id = %s""",
        (chat_id,),
    )
    row = cur.fetchone()
    cur.close()
    conn.close()
    if row and row["s"] is not None:
        return int(row["s"])
    return None


# ───────────────────────── کمکی‌ها ─────────────────────────
def _to_fa(text) -> str:
    return str(text).translate(str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹"))


def _format_duration(seconds) -> str:
    if seconds is None:
        return "ثبت نشده"
    days, rem = divmod(int(seconds), 86400)
    hours, rem = divmod(rem, 3600)
    minutes = rem // 60
    if days:
        return _to_fa(f"{days} روز و {hours} ساعت")
    if hours:
        return _to_fa(f"{hours} ساعت و {minutes} دقیقه")
    return _to_fa(f"{minutes} دقیقه")


def _is_owner(update: Update) -> bool:
    user = update.effective_user
    return user is not None and user.id == BOT_OWNER_ID


def _group_context(update: Update):
    chat = update.effective_chat
    message = update.effective_message
    if chat is None or message is None or chat.type == "private":
        return None, None
    return chat, message


# ───────────────────────── دستورات (فقط سازنده ربات) ─────────────────────────
# برای هر کاربر دیگر هیچ واکنشی نشان داده نمی‌شود.
async def install_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _is_owner(update):
        return
    chat, message = _group_context(update)
    if chat is None:
        return

    title = html.escape(chat.title or "بدون نام")
    try:
        added = _add_group(chat.id, chat.title, update.effective_user.id)
    except Exception as e:
        print(f"install_command DB error: {e}")
        await message.reply_text(DB_ERROR_TEXT)
        return

    text = INSTALL_OK_TEXT if added else INSTALL_EXISTS_TEXT
    await message.reply_text(
        text.format(title=title, chat_id=chat.id),
        parse_mode=ParseMode.HTML,
    )


async def uninstall_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _is_owner(update):
        return
    chat, message = _group_context(update)
    if chat is None:
        return

    title = html.escape(chat.title or "بدون نام")
    try:
        removed = _remove_group(chat.id)
    except Exception as e:
        print(f"uninstall_command DB error: {e}")
        await message.reply_text(DB_ERROR_TEXT)
        return

    text = UNINSTALL_OK_TEXT if removed else UNINSTALL_MISSING_TEXT
    await message.reply_text(
        text.format(title=title, chat_id=chat.id),
        parse_mode=ParseMode.HTML,
    )


async def leave_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _is_owner(update):
        return
    chat, message = _group_context(update)
    if chat is None:
        return

    seconds = None
    try:
        seconds = _presence_seconds(chat.id)
        _remove_group(chat.id)
    except Exception as e:
        print(f"leave_command DB error: {e}")

    await message.reply_text(
        LEAVE_TEXT.format(
            title=html.escape(chat.title or "بدون نام"),
            chat_id=chat.id,
            duration=_format_duration(seconds),
        ),
        parse_mode=ParseMode.HTML,
    )

    try:
        await context.bot.leave_chat(chat.id)
    except Exception as e:
        print(f"leave_chat error: {e}")
        await message.reply_text(LEAVE_FAILED_TEXT)