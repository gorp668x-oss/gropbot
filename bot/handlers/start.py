from telegram import Update
from telegram.ext import ContextTypes

from bot.database import get_connection
from bot.texts.welcome import WELCOME_TEXT
from bot.keyboards.main_menu import get_main_keyboard
from bot.utils.live_message import send_live_message

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    mention = f'<a href="tg://user?id={user.id}">𓄂꯭ꪰᴀ꯭ᷧᴍ꯭ⷨᴇ꯭ⷷʀ꯭ᷢ↬𓃮™</a>'

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

    final_text = WELCOME_TEXT.format(mention=mention)
    await send_live_message(
        update,
        context,
        final_text=final_text,
        reply_markup=get_main_keyboard(),
        parse_mode="HTML",
        delay=0.01
    )
