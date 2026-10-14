from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from bot.config import TELEGRAM_TOKEN
from bot.database import init_db, get_connection

WELCOME_TEXT = '''🔱 سلام {mention} 🌹

🗣️ من بات اکس هستم؛ رباتی برای مدیریت هوشمند گروه‌ها!

💎 بات اکس؛ توسعه هدفمند، عملکرد سنجیده، پیشرفت مداوم.

【 𝐃𝐄𝐕𝐄𝐋𝐎𝐏𝐄𝐃 𝐁𝐘 𓆩 𝐁𝐎𝐓 𝐗 𓆪 】'''

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    mention = user.mention_html()
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('''
        INSERT INTO users (user_id, username, first_name)
        VALUES (%s, %s, %s)
        ON CONFLICT (user_id) DO UPDATE SET
            username = EXCLUDED.username,
            first_name = EXCLUDED.first_name
    ''', (user.id, user.username, user.first_name))
    conn.commit()
    cur.close()
    conn.close()
    await update.message.reply_html(WELCOME_TEXT.format(mention=mention))

def main():
    init_db()
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
