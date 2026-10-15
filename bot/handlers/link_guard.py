import re
import asyncio
import time

from telegram import Update
from telegram.ext import ContextTypes

from bot.database import get_connection
from bot.utils.permissions import BOT_OWNER_ID


URL_PATTERN = re.compile(
    r'(https?://|www\.|t\.me/|telegram\.me/|telegram\.dog/|@[a-zA-Z0-9_]{3,})',
    re.IGNORECASE
)

# {chat_id: last_warning_timestamp}
_warn_cooldown = {}
COOLDOWN_SECONDS = 10


def is_locklink_enabled(chat_id: int) -> bool:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT lock_link FROM group_settings WHERE chat_id = %s", (chat_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return bool(row and row["lock_link"])


async def _delete_later(context, chat_id, message_id, seconds):
    await asyncio.sleep(seconds)
    try:
        await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
    except Exception:
        pass


def _can_send_warning(chat_id: int) -> bool:
    """چک می‌کنه آیا الان می‌تونه هشدار بفرسته یا نه"""
    now = time.time()
    last = _warn_cooldown.get(chat_id, 0)
    if now - last >= COOLDOWN_SECONDS:
        _warn_cooldown[chat_id] = now
        return True
    return False


async def link_guard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message
    chat = update.effective_chat
    user = update.effective_user

    if chat.type == "private" or not message or not user:
        return

    if not is_locklink_enabled(chat.id):
        return

    if user.id == BOT_OWNER_ID:
        return

    try:
        member = await context.bot.get_chat_member(chat.id, user.id)
        if member.status in ("administrator", "creator"):
            return
    except Exception:
        pass

    text = message.text or message.caption or ""
    has_link = bool(URL_PATTERN.search(text))

    has_url_button = False
    if message.reply_markup and hasattr(message.reply_markup, "inline_keyboard"):
        for row in message.reply_markup.inline_keyboard:
            for btn in row:
                if getattr(btn, "url", None):
                    has_url_button = True
                    break
            if has_url_button:
                break

    if not (has_link or has_url_button):
        return

    # پاک کردن پیام کاربر
    try:
        await message.delete()
    except Exception as e:
        print(f"Error deleting message: {e}")
        return

    # هشدار فقط اگه توی ۱۰ ثانیه اخیر هشدار نداده باشیم
    if not _can_send_warning(chat.id):
        return

    mention = user.mention_html()
    warn_text = (
        f"⫸ کاربر گرامی : {mention}\n\n"
        f"⌫ ارسال لینک در گروه ممنوع می‌باشد به همین دلیل پیام شما پاک شد !\n\n"
        f"◂ لطفاً از ارسال لینک خودداری فرمایید.\n\n"
        f"⋆ با تشکر از همکاری شما."
    )

    try:
        warn = await context.bot.send_message(
            chat_id=chat.id,
            text=warn_text,
            parse_mode="HTML"
        )
        asyncio.create_task(_delete_later(context, chat.id, warn.message_id, 10))
    except Exception as e:
        print(f"Error sending warning: {e}")