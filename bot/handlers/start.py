import asyncio
from telegram import Update
from telegram.ext import ContextTypes
from telegram.error import BadRequest, RetryAfter

from bot.database import get_connection
from bot.texts.welcome import WELCOME_TEXT
from bot.keyboards.main_menu import get_main_keyboard

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user is None or update.effective_message is None:
        return

    mention = (
        f'<a href="tg://user?id={user.id}">'
        '𓄂꯭ꪰᴀ꯭ᷧᴍ꯭ⷨᴇ꯭ⷷʀ꯭ᷢ↬𓃮™'
        '</a>'
    )

    # ثبت کاربر در دیتابیس
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

    # ارسال پیام اولیه خالی
    msg = await update.message.reply_text(".")

    # تقسیم متن به خطوط برای تایپ تدریجی
    lines = final_text.split('\n')
    current_text = ""

    for i, line in enumerate(lines):
        if current_text:
            current_text += "\n" + line
        else:
            current_text = line

        # اگر خط خالی بود، فقط یک خط جدید اضافه کن
        if line == "":
            try:
                await msg.edit_text(current_text, parse_mode="HTML")
            except Exception:
                pass
            await asyncio.sleep(0.1)
            continue

        try:
            # ویرایش پیام با متن تا این خط
            await msg.edit_text(current_text, parse_mode="HTML")
        except BadRequest as e:
            if "not modified" not in str(e).lower():
                pass
        except RetryAfter as e:
            await asyncio.sleep(e.retry_after)
        except Exception:
            pass

        # تاخیر ایمن برای جلوگیری از بلاک شدن توسط تلگرام
        await asyncio.sleep(0.4)

    # ارسال نهایی با دکمه‌ها
    try:
        await msg.edit_text(
            final_text,
            parse_mode="HTML",
            reply_markup=get_main_keyboard(),
            disable_web_page_preview=True
        )
    except BadRequest:
        try:
            await update.message.reply_html(
                final_text,
                reply_markup=get_main_keyboard()
            )
        except Exception:
            pass
    except Exception:
        pass
