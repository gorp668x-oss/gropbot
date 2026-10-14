from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from bot.config import TELEGRAM_TOKEN
from bot.database import init_db, get_connection

WELCOME_TEXT = """🔱 سلام {mention} 🌹

💬 من <b>بات اکس</b> هستم؛ رباتی هوشمند برای مدیریت آسان و سریع گروه‌ها!

⚜️ <b>امکانات من :</b>

<b>🧠 سیستم‌های هوشمند و کاربردی</b>
<b>🚀 سرعت بالا و عملکرد بهینه</b>
<b>🔰 ابزارهای امنیتی و ضد مزاحمت</b>
<b>🛠 قفل‌های متنوع و مدیریت پیشرفته</b>
<b>💡 قابلیت‌های اختصاصی و کاربردی</b>
<b>🌟 خوش‌آمدگویی و بهبود تجربه کاربران</b>
<b>📊 قابلیت ارائه آمار و اطلاعات</b>

🔥 <b>چرا بات اکس؟</b>

<b>✅ توسعه اختصاصی توسط تیم بات اکس</b>
<b>✅ تمرکز بر سرعت و پایداری</b>
<b>✅ بهینه‌سازی و رفع خطاها</b>
<b>✅ بدون تبلیغات مزاحم، در نسخه‌های پشتیبانی‌شده</b>
<b>✅ حفظ محرمانگی اطلاعات و کدها</b>
<b>🏅 بیش از ۷ سال تجربه، در صورت تأیید سابقه تیم</b>

💎 امنیت و کیفیت، اولویت ماست.

❤️ مدیریت گروهت رو هوشمندانه‌تر تجربه کن!

🔐 توسعه مستقل، دقت در اجرا و پیشرفت مداوم.

【 Licenced By  🄱🄾🅃🅇 】"""

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