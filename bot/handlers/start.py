from telegram import Update
from telegram.ext import ContextTypes

from bot.database import get_connection
from bot.texts.welcome import WELCOME_TEXT
from bot.keyboards.main_menu import get_main_keyboard
from bot.utils.live_message import send_live_message

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user is None or update.effective_message is None:
        return

    mention = (
        f'<a href="tg://user?id={user.id}">'
        '𓄂꯭ꪰᴀ꯭ᷧᴍ꯭ⷨᴇ꯭ⷷʀ꯭ᷢ↬𓃮™'
        '</a>'
    )

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
    
    # استفاده از تابع جدید (نه روش قدیمی)
    await send_live_message(
        bot=context.bot,
        chat_id=update.effective_chat.id,
        final_text=final_text,
        reply_markup=get_main_keyboard(),
        parse_mode="HTML",
        delay=0.01,
        reply_to_message_id=update.message.message_id
    )
