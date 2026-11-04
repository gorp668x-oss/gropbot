import asyncio
import re
from telegram import Update
from telegram.ext import ContextTypes
from telegram.error import BadRequest

from bot.database import get_connection
from bot.texts.welcome import WELCOME_TEXT
from bot.keyboards.main_menu import get_main_keyboard

def strip_html(text):
    """حذف تگ‌های HTML برای نمایش تدریجی بدون خطا"""
    return re.sub(r'<[^>]+>', '', text)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user is None or update.effective_message is None:
        return

    display_name = user.first_name
    mention = f'<a href="tg://user?id={user.id}">{display_name}</a>'

    conn = None
    cur = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO users (user_id, username, first_name)
            VALUES (%s, %s, %s)
            ON CONFLICT (user_id) DO UPDATE SET
                username = EXCLUDED.username,
                first_name = EXCLUDED.first_name
        """, (user.id, user.username, user.first_name))
        conn.commit()
    except Exception as e:
        print(f"Database error in start: {e}")
    finally:
        if cur: cur.close()
        if conn: conn.close()

    final_text = WELCOME_TEXT.format(mention=mention)
    plain_text = strip_html(final_text)

    # ۱. ارسال پیام اولیه
    msg = await update.message.reply_text("⌨️")

    # ۲. تایپ تدریجی با تکه‌های بزرگتر و سرعت بالا
    current_text = ""
    chunk_size = 35

    for i in range(0, len(plain_text), chunk_size):
        current_text += plain_text[i:i + chunk_size]
        try:
            await msg.edit_text(current_text)
        except BadRequest as e:
            if "not modified" not in str(e).lower():
                pass
        except Exception:
            pass
        await asyncio.sleep(0.08)

    # ۳. نمایش نهایی با HTML و دکمه‌ها
    try:
        await msg.edit_text(
            final_text,
            parse_mode="HTML",
            reply_markup=get_main_keyboard(),
            disable_web_page_preview=True
        )
    except BadRequest:
        try:
            await msg.edit_reply_markup(reply_markup=get_main_keyboard())
        except Exception:
            pass
    except Exception:
        pass
