from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from bot.config import TELEGRAM_TOKEN
from bot.database import init_db, get_connection

WELCOME_TEXT = """〽️ سلام {mention} 🌹

💬 من <b>بات اکس</b> هستم؛ فراتر از یک ربات، یک سیستم قدرتمند برای مدیریت هوشمند گروه‌ها!

🚀 <b>تفاوت ما با دیگران فقط در حرف نیست؛ در عملکرد ماست!</b>

⚙️ <b>امکانات و قابلیت‌های بات اکس:</b>

🧠 مجهز به سیستم هوش مصنوعی (AI)
🕵️ دارای سیستم TIG ضد ممبر دزد
⚔️ دارای سیستم ABM ضد خیانت
💰 دارای سیستم درآمدزایی از گروه
🔞 شناسایی رسانه‌های +18
🔍 دارای سامانه تشخیص تبچی
🔐 مجهز به انواع قفل‌های مدیریتی
➕ دارای قابلیت اد اجباری
📢 دارای عضویت اجباری در کانال
👋 دارای خوش‌آمدگویی هوشمند
📊 ارائه آمار روزانه و ماهانه
⚡ سرعت بالا و عملکرد بهینه
🖥️ زیرساخت اختصاصی
🧪 امکان تست پیش از انتخاب

💥 <b>چرا بات اکس؟</b>

🔸 تمرکز بر سرعت، امنیت و پایداری
🔸 توسعه و برنامه‌نویسی اختصاصی
🔸 بهینه‌سازی مستمر و کاهش خطاها
🔸 طراحی متناسب با نیاز پروژه
🔸 خلاقیت، نوآوری و پیشرفت مداوم
🔸 حفظ محرمانگی کدها و جزئیات فنی
🏅 بیش از ۷ سال تجربه، در صورت تأیید سابقه تیم

🖥️ برنامه‌نویسی و توسعه توسط <b>تیم بات اکس</b>

⚜️ <i>وقتی کیفیت حرف می‌زنه، نیازی به ادعا نیست.</i>

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