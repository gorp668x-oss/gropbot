import random
import asyncio
from datetime import datetime

import jdatetime
from telegram import Update
from telegram.ext import ContextTypes

from bot.database import get_connection


# ============================================================
# دسته‌بندی ایموجی‌ها برای تنوع
# ============================================================
EMOJI_GREETING = ["💐", "🌸", "🌹", "🌷", "🌺", "💮", "🏵️", "🌻", "🌼", "🪷", "🍀", "🎉", "🎊", "✨", "🌟"]
EMOJI_WELCOME = ["🌸", "🌼", "🌺", "💐", "🌷", "🌹", "🪷", "🌻", "✨", "💫", "⭐", "🌟", "🎈", "🎀", "💝"]
EMOJI_TIME = ["⏱️", "⏰", "🕐", "🕑", "🕒", "⌚", "⏳", "🕰️", "🕓", "🕔", "🕕"]
EMOJI_DATE = ["📆", "📅", "🗓️", "📇", "📋", "📌", "📍"]


def get_random_greeting():
    return random.choice(EMOJI_GREETING)

def get_random_welcome():
    return random.choice(EMOJI_WELCOME)

def get_random_time():
    return random.choice(EMOJI_TIME)

def get_random_date():
    return random.choice(EMOJI_DATE)


def to_persian_digits(s):
    """تبدیل اعداد لاتین به فارسی"""
    trans = str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹")
    return str(s).translate(trans)


def get_persian_date():
    """تاریخ و ساعت شمسی"""
    now = datetime.now()
    jdate = jdatetime.datetime.fromgregorian(datetime=now)

    # روز هفته به فارسی
    weekdays = {
        0: "شنبه",
        1: "یکشنبه",
        2: "دوشنبه",
        3: "سه‌شنبه",
        4: "چهارشنبه",
        5: "پنجشنبه",
        6: "جمعه",
    }
    weekday = weekdays[jdate.weekday()]

    # ماه‌های شمسی
    months = {
        1: "فروردین", 2: "اردیبهشت", 3: "خرداد",
        4: "تیر", 5: "مرداد", 6: "شهریور",
        7: "مهر", 8: "آبان", 9: "آذر",
        10: "دی", 11: "بهمن", 12: "اسفند",
    }
    month = months[jdate.month]

    # ساعت و دقیقه
    hour = to_persian_digits(f"{jdate.hour:02d}")
    minute = to_persian_digits(f"{jdate.minute:02d}")

    date_str = f"{weekday} {to_persian_digits(jdate.day)} {month} {to_persian_digits(jdate.year)}"
    time_str = f"{hour}:{minute}"

    return time_str, date_str


def is_welcome_enabled(chat_id: int) -> bool:
    """چک می‌کنه خوش‌آمدگویی توی این گروه فعاله یا نه (پیش‌فرض: فعال)"""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS group_settings (
            chat_id BIGINT PRIMARY KEY,
            lock_link BOOLEAN DEFAULT FALSE,
            welcome_enabled BOOLEAN DEFAULT TRUE
        )
    """)
    # اگه ستون welcome_enabled وجود نداشت اضافه کن
    try:
        cur.execute("ALTER TABLE group_settings ADD COLUMN welcome_enabled BOOLEAN DEFAULT TRUE")
        conn.commit()
    except Exception:
        conn.rollback()

    cur.execute("SELECT welcome_enabled FROM group_settings WHERE chat_id = %s", (chat_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()

    # پیش‌فرض فعال
    if row is None or row["welcome_enabled"] is None:
        return True
    return bool(row["welcome_enabled"])


async def _delete_later(context, chat_id, message_id, seconds):
    await asyncio.sleep(seconds)
    try:
        await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
    except Exception:
        pass


async def welcome_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """وقتی کاربر جدید وارد گروه می‌شه"""
    message = update.effective_message
    chat = update.effective_chat

    if not message or not message.new_chat_members:
        return

    # حذف پیام سیستمی «X به گروه پیوست»
    try:
        await message.delete()
    except Exception:
        pass

    # چک فعال بودن خوش‌آمدگویی
    if not is_welcome_enabled(chat.id):
        return

    # زمان و تاریخ
    time_str, date_str = get_persian_date()

    for member in message.new_chat_members:
        # اگه خود ربات اضافه شد، خوش‌آمد نگو
        if member.id == context.bot.id:
            continue

        # منشن کاربر
        mention = member.mention_html()

        # متن خوش‌آمدگویی با ایموجی‌های تصادفی
        text = (
            f"سلام {mention} عزیز {get_random_greeting()}\n"
            f"به گروه {chat.title} خوش اومدین {get_random_welcome()}\n\n"
            f"{get_random_time()} زمان ورود : {time_str}\n"
            f"{get_random_date()} تاریخ ورود : {date_str}"
        )

        try:
            welcome_msg = await context.bot.send_message(
                chat_id=chat.id,
                text=text,
                parse_mode="HTML"
            )
            # پاک کردن پیام خوش‌آمدگویی بعد از ۱ دقیقه (اختیاری)
            # asyncio.create_task(_delete_later(context, chat.id, welcome_msg.message_id, 60))
        except Exception as e:
            print(f"Error sending welcome message: {e}")