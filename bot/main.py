from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from bot.config import TELEGRAM_TOKEN
from bot.database import init_db, get_connection

WELCOME_TEXT = """🔱 سلام {mention} 🌹

💬 من <b>بات اکس</b> هستم؛ رباتی هوشمند برای مدیریت آسان و سریع گروه‌ها!

⚜️ <b>امکانات من :</b>

🧠 سیستم‌های هوشمند و کاربردی
🚀 سرعت بالا و عملکرد بهینه
🔰 ابزارهای امنیتی و ضد مزاحمت
🛠 قفل‌های متنوع و مدیریت پیشرفته
💡 قابلیت‌های اختصاصی و کاربردی
🌟 خوش‌آمدگویی و بهبود تجربه کاربران
📊 قابلیت ارائه آمار و اطلاعات

🔥 <b>چرا بات اکس؟</b>

✅ توسعه اختصاصی توسط تیم بات اکس
✅ تمرکز بر سرعت و پایداری
✅ بهینه‌سازی و رفع خطاها
✅ بدون تبلیغات مزاحم، در نسخه‌های پشتیبانی‌شده
✅ حفظ محرمانگی اطلاعات و کدها
🏅 بیش از ۷ سال تجربه، در صورت تأیید سابقه تیم

💎 امنیت و کیفیت، اولویت ماست.

❤️ مدیریت گروهت رو هوشمندانه‌تر تجربه کن!

🔐 توسعه مستقل، دقت در اجرا و پیشرفت مداوم.

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