from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from bot.config import TELEGRAM_TOKEN
from bot.database import init_db, get_connection

WELCOME_TEXT = """🔱 سلام {mention} 🌹

🗣️ من <b>بات اکس</b> هستم؛ رباتی برای مدیریت هوشمند گروه‌ها.

⚜️ <b>ویژگی‌های ما</b>
🧠 هوشمند و سریع
🚀 بهینه و پایدار
🔰 امن و مطمئن
💻 توسعه اختصاصی توسط تیم بات اکس

💠 <b>چرا بات اکس؟</b>
🏅 بیش از ۷ سال تجربه
🧩 طراحی بر اساس نیاز پروژه
⚙️ پایداری و مدیریت منابع
🛠️ رفع خطا و بهینه‌سازی مستمر
💡 قابلیت‌های اختصاصی
🌟 بهبود تجربه کاربری
🎯 کیفیت و نگهداری آسان

🔐 محرمانگی، دقت و بهبود مستمر؛ اصول کاری ما.

🔏 <b>مالکیت فکری | بات اکس</b>
📜 کدها و مستندات متعلق به تیم بات اکس است.
🚫 کپی‌برداری ناقض حقوق، قابل پیگیری قانونی است.

👑 مسیر ما: توسعه مستقل و یادگیری مستمر.

💎 <b>بات اکس؛ توسعه هدفمند، عملکرد سنجیده.</b>

🏆 <i>وقتی کیفیت حرف می‌زنه، نیازی به ادعا نیست.</i>

【 𝐃𝐄𝐕𝐄𝐋𝐎𝐏𝐄𝐃 𝐁𝐘 𓆩 𝐁𝐎𝐓 𝐗 𓆪 】"""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    mention = user.mention_html()

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

    await update.message.reply_html(WELCOME_TEXT.format(mention=mention))

def main():
    init_db()
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()