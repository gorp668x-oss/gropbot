from telegram import Update
from telegram.ext import ContextTypes
from bot.database import get_connection
from bot.texts.welcome import WELCOME_TEXT
from bot.keyboards.main_menu import get_main_keyboard

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

    await update.message.reply_html(
        final_text,
        reply_markup=get_main_keyboard(),
        disable_web_page_preview=True
    )
