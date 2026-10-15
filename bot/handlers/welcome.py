import random
import asyncio
from datetime import datetime, timezone, timedelta

import jdatetime
from telegram import Update
from telegram.ext import ContextTypes

from bot.database import get_connection


# ============================================================
# ایموجی‌های تصادفی برای تنوع
# ============================================================
EMOJI_GREETING = ["💐", "🌸", "🌹", "🌷", "🌺", "💮", "🏵️", "🌻", "🌼", "🪷", "🍀", "🎉", "🎊", "✨", "🌟"]
EMOJI_WELCOME = ["🌸", "🌼", "🌺", "💐", "🌷", "🌹", "🪷", "🌻", "✨", "💫", "⭐", "🌟", "🎈", "🎀", "💝"]
EMOJI_TIME = ["⏱️", "⏰", "🕐", "🕑", "🕒", "⌚", "⏳", "🕰️", "🕓", "🕔", "🕕"]
EMOJI_DATE = ["📆", "📅", "🗓️", "📇", "📋", "📌", "📍"]


def rnd(arr):
    return random.choice(arr)


def to_persian_digits(s):
    trans = str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹")
    return str(s).translate(trans)


def get_iran_time():
    """زمان دقیق ایران"""
    iran_tz = timezone(timedelta(hours=3, minutes=30))
    return datetime.now(iran_tz)


def get_persian_date():
    """تاریخ و ساعت شمسی دقیق ایران"""
    now = get_iran_time()
    jdate = jdatetime.datetime.fromgregorian(datetime=now)

    weekdays = {
        0: "شنبه", 1: "یکشنبه", 2: "دوشنبه",
        3: "سه‌شنبه", 4: "چهارشنبه", 5: "پنجشنبه", 6: "جمعه",
    }
    months = {
        1: "فروردین", 2: "اردیبهشت", 3: "خرداد",
        4: "تیر", 5: "مرداد", 6: "شهریور",
        7: "مهر", 8: "آبان", 9: "آذر",
        10: "دی", 11: "بهمن", 12: "اسفند",
    }

    weekday = weekdays[jdate.weekday()]
    month = months[jdate.month]

    hour = to_persian_digits(f"{jdate.hour:02d}")
    minute = to_persian_digits(f"{jdate.minute:02d}")

    date_str = f"{weekday} {to_persian_digits(jdate.day)} {month} {to_persian_digits(jdate.year)}"
    time_str = f"{hour}:{minute}"

    return time_str, date_str


# ============================================================
# تنظیمات گروه
# ============================================================
def _ensure_table():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS group_settings (
            chat_id BIGINT PRIMARY KEY,
            lock_link BOOLEAN DEFAULT FALSE,
            welcome_enabled BOOLEAN DEFAULT TRUE
        )
    """)
    try:
        cur.execute("ALTER TABLE group_settings ADD COLUMN welcome_enabled BOOLEAN DEFAULT TRUE")
        conn.commit()
    except Exception:
        conn.rollback()
    conn.commit()
    cur.close()
    conn.close()


def is_welcome_enabled(chat_id: int) -> bool:
    _ensure_table()
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT welcome_enabled FROM group_settings WHERE chat_id = %s", (chat_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    if row is None or row["welcome_enabled"] is None:
        return True
    return bool(row["welcome_enabled"])


def set_welcome(chat_id: int, enabled: bool):
    _ensure_table()
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO group_settings (chat_id, welcome_enabled)
        VALUES (%s, %s)
        ON CONFLICT (chat_id) DO UPDATE SET welcome_enabled = EXCLUDED.welcome_enabled
    """, (chat_id, enabled))
    conn.commit()
    cur.close()
    conn.close()


# ============================================================
# خوش‌آمدگویی
# ============================================================
async def welcome_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message
    chat = update.effective_chat

    if not message or not message.new_chat_members:
        return

    # حذف پیام سیستمی
    try:
        await message.delete()
    except Exception:
        pass

    if not is_welcome_enabled(chat.id):
        return

    time_str, date_str = get_persian_date()
    group_name = chat.title or "گروه"

    for member in message.new_chat_members:
        if member.id == context.bot.id:
            continue

        mention = member.mention_html()

        text = (
            f"سلام {mention} عزیز {rnd(EMOJI_GREETING)}\n"
            f"به گروه <b>{group_name}</b> خوش اومدین {rnd(EMOJI_WELCOME)}\n\n"
            f"{rnd(EMOJI_TIME)} زمان ورود : {time_str}\n"
            f"{rnd(EMOJI_DATE)} تاریخ ورود : {date_str}"
        )

        try:
            await context.bot.send_message(
                chat_id=chat.id,
                text=text,
                parse_mode="HTML"
            )
        except Exception as e:
            print(f"Error sending welcome: {e}")


# ============================================================
# دستورات خوشامد
# ============================================================
async def welcome_on_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from bot.utils.permissions import is_admin_or_owner

    chat = update.effective_chat
    message = update.effective_message

    if chat.type == "private":
        return

    if not await is_admin_or_owner(update, context):
        return

    if is_welcome_enabled(chat.id):
        await message.reply_text("⋅• خوش‌ آمدگویی از قبل فعال است !")
        return

    set_welcome(chat.id, True)
    await message.reply_text("⋅• ارسال پیام خوش‌ آمدگویی فعال شد !")


async def welcome_off_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from bot.utils.permissions import is_admin_or_owner

    chat = update.effective_chat
    message = update.effective_message

    if chat.type == "private":
        return

    if not await is_admin_or_owner(update, context):
        return

    if not is_welcome_enabled(chat.id):
        await message.reply_text("•⋅ خوش‌ آمدگویی از قبل غیرفعال است !")
        return

    set_welcome(chat.id, False)
    await message.reply_text("•⋅ ارسال پیام خوش‌ آمدگویی غیرفعال شد !")