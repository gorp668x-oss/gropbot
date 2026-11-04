import asyncio
import time
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

    # ثبت کاربر
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
        print(f"Database error: {e}")
    finally:
        if cur: cur.close()
        if conn: conn.close()

    final_text = WELCOME_TEXT.format(mention=mention)

    # فقط توی چت خصوصی از Draft استفاده کن
    if update.effective_chat.type == "private":
        draft_id = int(time.time() * 1000) % 2147483647
        if draft_id == 0: draft_id = 1
        
        # شبیه‌سازی تایپ با sendMessageDraft
        words = final_text.split(' ')
        accumulated = ""
        last_update = 0
        
        for i, word in enumerate(words):
            accumulated += word + " "
            now = time.monotonic()
            # هر ۸۰ میلی‌ثانیه یکبار آپدیت کن تا ریت‌لیمیت نخوری
            if now - last_update >= 0.08 or i == len(words) - 1:
                try:
                    await context.bot.send_message_draft(
                        chat_id=update.effective_chat.id,
                        draft_id=draft_id,
                        text=accumulated
                    )
                    last_update = now
                except Exception as e:
                    print(f"Draft error: {e}")
                    break
        
        # پیام نهایی با دکمه‌ها (Draft رو جایگزین می‌کنه)
        try:
            await update.message.reply_html(
                final_text,
                reply_markup=get_main_keyboard()
            )
        except Exception:
            pass
    else:
        # توی گروه‌ها همون روش قدیمی
        await update.message.reply_html(
            final_text,
            reply_markup=get_main_keyboard()
        )
