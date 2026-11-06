import html
import secrets
import time

import psycopg
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ApplicationHandlerStop, ContextTypes

from bot.database import get_connection
from bot.keyboards.support import (
    get_support_keyboard,
    get_ticket_prompt_keyboard,
    get_after_ticket_keyboard,
)
from bot.texts.support import (
    SUPPORT_TEXT,
    TICKET_PROMPT_TEXT,
    TICKET_SENT_TEXT,
    TICKET_OWNER_TEXT,
    TICKET_REPLY_TEXT,
)
from bot.utils.permissions import BOT_OWNER_ID
from bot.utils.screen import show_screen

TICKET_WINDOW = 600      # ثانیه؛ مدت فعال بودن حالت ارسال پیام
TICKET_COOLDOWN = 20     # ثانیه؛ فاصله بین دو پیام یک کاربر
MAX_LEN = 3000           # حداکثر طول پیام

TOAST_SUPPORT = "🎧 به بخش پشتیبانی خوش آمدید"
TOAST_TICKET = "📨 به بخش پشتیبانی غیرمستقیم خوش آمدید"

_last_ticket = {}


# ───────────────────────── دیتابیس ─────────────────────────
def _ensure_table():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS tickets (
            id SERIAL PRIMARY KEY,
            code TEXT UNIQUE NOT NULL,
            user_id BIGINT NOT NULL,
            username TEXT,
            first_name TEXT,
            message TEXT NOT NULL,
            owner_message_id BIGINT,
            status TEXT DEFAULT 'open',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    cur.close()
    conn.close()


def _create_ticket(user, text) -> str:
    _ensure_table()
    conn = get_connection()
    cur = conn.cursor()
    try:
        for _ in range(5):
            code = "TK-" + secrets.token_hex(3).upper()
            try:
                cur.execute(
                    """INSERT INTO tickets (code, user_id, username, first_name, message)
                       VALUES (%s, %s, %s, %s, %s)""",
                    (code, user.id, user.username, user.first_name, text),
                )
                conn.commit()
                return code
            except psycopg.errors.UniqueViolation:
                conn.rollback()
        raise RuntimeError("could not generate ticket code")
    finally:
        cur.close()
        conn.close()


def _update_ticket(code, **fields):
    conn = get_connection()
    cur = conn.cursor()
    sets = ", ".join(f"{k} = %s" for k in fields)
    cur.execute(f"UPDATE tickets SET {sets} WHERE code = %s", (*fields.values(), code))
    conn.commit()
    cur.close()
    conn.close()


def _find_by_owner_message(owner_message_id: int):
    _ensure_table()
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT code, user_id FROM tickets WHERE owner_message_id = %s",
        (owner_message_id,),
    )
    row = cur.fetchone()
    cur.close()
    conn.close()
    return (row["code"], row["user_id"]) if row else None


# ───────────────────────── دکمه‌ها ─────────────────────────
async def support_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    if query.data == "support":
        context.user_data.pop("ticket_until", None)
        await show_screen(update, context, SUPPORT_TEXT, get_support_keyboard(), TOAST_SUPPORT)
    elif query.data == "support_ticket":
        context.user_data["ticket_until"] = time.time() + TICKET_WINDOW
        await show_screen(update, context, TICKET_PROMPT_TEXT, get_ticket_prompt_keyboard(), TOAST_TICKET)
    else:
        await query.answer()


# ───────────────────────── پیام‌های متنی پیوی ─────────────────────────
async def ticket_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message
    user = update.effective_user
    if not message or not user or not message.text:
        return

    # ۱) پاسخ سازنده (ریپلای روی پیام تیکت)
    if user.id == BOT_OWNER_ID and message.reply_to_message:
        ticket = _find_by_owner_message(message.reply_to_message.message_id)
        if ticket:
            code, target_id = ticket
            try:
                await context.bot.send_message(
                    target_id,
                    TICKET_REPLY_TEXT.format(code=code, text=html.escape(message.text)),
                    parse_mode=ParseMode.HTML,
                )
                _update_ticket(code, status="answered")
                await message.reply_text(f"✅ پاسخ برای تیکت {code} ارسال شد.")
            except Exception as e:
                await message.reply_text(f"❌ ارسال پاسخ ناموفق بود:\n{e}")
            raise ApplicationHandlerStop
        return

    # ۲) کاربر در حالت پشتیبانی غیرمستقیم
    if time.time() > context.user_data.get("ticket_until", 0):
        return

    if len(message.text) > MAX_LEN:
        await message.reply_text("⚠️ پیام شما بیش از حد طولانی است. لطفاً کوتاه‌تر بنویسید.")
        raise ApplicationHandlerStop

    now = time.time()
    if now - _last_ticket.get(user.id, 0) < TICKET_COOLDOWN:
        await message.reply_text("⏳ لطفاً چند لحظه صبر کنید و دوباره تلاش کنید.")
        raise ApplicationHandlerStop
    _last_ticket[user.id] = now

    try:
        code = _create_ticket(user, message.text)
    except Exception as e:
        print(f"Ticket DB error: {e}")
        await message.reply_text("❌ خطا در ثبت پیام. لطفاً بعداً دوباره تلاش کنید.")
        raise ApplicationHandlerStop

    try:
        owner_msg = await context.bot.send_message(
            BOT_OWNER_ID,
            TICKET_OWNER_TEXT.format(
                code=code,
                user_id=user.id,
                name=html.escape(user.first_name or "کاربر"),
                username=f"@{user.username}" if user.username else "ندارد",
                text=html.escape(message.text),
            ),
            parse_mode=ParseMode.HTML,
        )
        _update_ticket(code, owner_message_id=owner_msg.message_id)
    except Exception as e:
        print(f"Ticket delivery error: {e}")
        _update_ticket(code, status="undelivered")
        await message.reply_text("❌ ارسال ناموفق بود. لطفاً از «پشتیبانی مستقیم» استفاده کنید.")
        raise ApplicationHandlerStop

    context.user_data.pop("ticket_until", None)

    sent_text = TICKET_SENT_TEXT.format(code=code)
    await message.reply_text(
        sent_text,
        parse_mode=ParseMode.HTML,
        reply_markup=get_after_ticket_keyboard(),
    )
    raise ApplicationHandlerStop