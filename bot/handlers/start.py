import asyncio
from telegram import Update
from telegram.ext import ContextTypes

from bot.database import get_connection
from bot.texts.welcome import WELCOME_TEXT
from bot.keyboards.main_menu import get_main_keyboard

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    mention = f'<a href="tg://user?id={user.id}">𓄂꯭ꪰᴀ꯭ᷧᴍ꯭ⷨᴇ꯭ⷷʀ꯭ᷢ↬𓃮™</a>'

    # ثبت کاربر در دیتابیس
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
    cur.close()
    conn.close()

    # متن نهایی
    final_text = WELCOME_TEXT.format(mention=mention)

    # ارسال پیام اول خالی
    msg = await update.message.reply_html(".")

    # انیمیشن تایپ سریع (ویرایشی)
    step = max(1, len(final_text) // 30) # 30 مرحله برای سرعت بالا
    i = step
    while i < len(final_text):
        chunk = final_text[:i]
        try:
            await msg.edit_text(chunk, parse_mode="HTML")
        except Exception:
            pass
        await asyncio.sleep(0.03) # تاخیر خیلی کم
        i += step

    # در نهایت نمایش متن کامل همراه با دکمه‌ها
    try:
        await msg.edit_text(
            final_text,
            parse_mode="HTML",
            reply_markup=get_main_keyboard()
        )
    except Exception:
        await update.message.reply_html(
            final_text,
            reply_markup=get_main_keyboard()
        )
