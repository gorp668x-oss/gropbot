import random
import asyncio
from datetime import datetime, timezone, timedelta

import jdatetime
from telegram import Update
from telegram.ext import ContextTypes

from bot.database import get_connection
from bot.handlers.edit_mode import is_edit_mode_enabled


# ============================================================
# ایموجی‌های تصادفی
# ============================================================
EMOJI_GREETING = ["💐", "🌸", "🌹", "🌷", "🌺", "💮", "🏵️", "🌻", "🌼", "🪷", "🍀", "🎉", "🎊", "✨", "🌟"]
EMOJI_WELCOME = ["🌸", "🌼", "🌺", "💐", "🌷", "🌹", "🪷", "🌻", "✨", "💫", "⭐", "🌟", "🎈", "🎀", "💝"]
EMOJI_TIME = ["⏱️", "⏰", "🕐", "🕑", "🕒", "⌚", "⏳", "🕰️", "🕓", "🕔", "🕕"]
EMOJI_DATE = ["📆", "📅", "🗓️", "📇", "📋", "📌", "📍"]

# جلوگیری از ارسال چندباره خوش آمدگویی
_welcome_cooldown = {}


def rnd(arr):
    return random.choice(arr)


def to_persian_digits(s):
    trans = str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹")
    return str(s).translate(trans)


def get_iran_time():
    iran_tz = timezone(timedelta(hours=3, minutes=30))
    return datetime.now(iran_tz)


def get_persian_date():
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
# انیمیشن تایپ روی خوشامد
# ============================================================
async def _send_with_typing(context, chat_id: int, text: str):
    """پیام رو با انیمیشن تایپ سریع می‌فرسته"""
    try:
        # پیام اول خالی با یه نقطه
        msg = await context.bot.send_message(chat_id=chat_id, text=".")

        # سرعت خیلی زیاد — هر ۰.۰۵ ثانیه یه کاراکتر (یا بیشتر)
        # چون پیام طولانیه، پله‌پله اضافه می‌کنیم که خیلی سریع باشه
        step = max(1, len(text) // 25)  # ۲۵ مرحله برای رسیدن به متن کامل

        i = step
        while i < len(text):
            chunk = text[:i]
            try:
                await msg.edit_text(chunk, parse_mode="HTML")
            except Exception:
                pass
            await asyncio.sleep(0.05)
            i += step

        # متن کامل
        try:
            await msg.edit_text(text, parse_mode="HTML")
        except Exception:
            pass

    except Exception as e:
        print(f"Error in typing animation: {e}")


async def _send_simple(context, chat_id: int, text: str):
    """ارسال ساده بدون انیمیشن"""
    try:
        await context.bot.send_message(chat_id=chat_id, text=text, parse_mode="HTML")
    except Exception as e:
        print(f"Error sending welcome: {e}")


# ============================================================
# خوش‌آمدگویی
# ============================================================
async def welcome_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message
    chat = update.effective_chat

    if not message or not message.new_chat_members:
        return

    try:
        await message.delete()
    except Exception:
        pass

    if not is_welcome_enabled(chat.id):
        return

    time_str, date_str = get_persian_date()
    group_name = chat.title or "گروه"

    import time
    current_time = time.time()

    for member in message.new_chat_members:
        if member.id == context.bot.id:
            continue

        # اگر عضو جدید یک ربات بود
        if member.is_bot:
            try:
                # بن کردن ربات
                await context.bot.ban_chat_member(chat_id=chat.id, user_id=member.id)
                
                # ارسال پیام اعلامیه
                bot_name = member.first_name
                alert_text = (
                    f"⚠️ <b>هشدار امنیتی</b>\n\n"
                    f"ربات مخرب <b>{bot_name}</b> توسط یکی از اعضا به گروه اضافه شد.\n"
                    f"ربات بات اکس بلافاصله این ربات را <b>بن</b> کرد."
                )
                await context.bot.send_message(chat_id=chat.id, text=alert_text, parse_mode="HTML")
            except Exception as e:
                print(f"Error banning bot: {e}")
            continue # ادامه حلقه برای بقیه اعضا

        # چک کردن اینکه تو 10 ثانیه اخیر برای این کاربر پیام نفرستاده باشیم
        last_welcome = _welcome_cooldown.get(member.id, 0)
        if current_time - last_welcome < 10:
            continue
        _welcome_cooldown[member.id] = current_time

        mention = member.mention_html()

        text = (
            f"⋅• سلام {mention} عزیز {rnd(EMOJI_GREETING)}\n"
            f"به گروه <b>{group_name}</b> خوش اومدین {rnd(EMOJI_WELCOME)}\n\n"
            f"{rnd(EMOJI_TIME)} زمان ورود : ( {time_str} )\n"
            f"{rnd(EMOJI_DATE)} تاریخ ورود : ( {date_str} )"
        )

        if is_edit_mode_enabled(chat.id):
            # با انیمیشن تایپ سریع
            asyncio.create_task(_send_with_typing(context, chat.id, text))
        else:
            # ساده
            asyncio.create_task(_send_simple(context, chat.id, text))


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