from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from bot.config import TELEGRAM_TOKEN
from bot.database import init_db, get_connection

WELCOME_TEXT = """🔱 سلام {mention} 🌹

<b>🗣️ من بات اکس هستم؛ فراتر از یک ربات، یک سیستم قدرتمند برای مدیریت هوشمند گروه‌ها!</b>

🚀 تفاوت ما با دیگران فقط در حرف نیست؛ در عملکرد ماست!

⚙️ امکانات و قابلیت‌های بات اکس:

<b>🧠 مجهز به سیستم هوش مصنوعی (AI)</b>
<b>🕵️ دارای سیستم TIG ضد ممبر دزد</b>
<b>⚔️ دارای سیستم ABM ضد خیانت</b>
<b>💰 دارای سیستم درآمدزایی از گروه</b>
<b>🔞 شناسایی رسانه‌های +18</b>
<b>🔍 دارای سامانه تشخیص تبچی</b>
<b>🔐 مجهز به انواع قفل‌های مدیریتی</b>
<b>➕ دارای قابلیت اد اجباری</b>
<b>📢 دارای عضویت اجباری در کانال</b>
<b>👋 دارای خوش‌آمدگویی هوشمند</b>
<b>📊 ارائه آمار روزانه و ماهانه</b>
<b>⚡️ سرعت بالا و عملکرد بهینه</b>
<b>🖥 زیرساخت اختصاصی</b>
<b>🔬 امکان تست پیش از انتخاب</b>

<b>💥 چرا بات اکس؟</b>

<b>✅ تمرکز بر سرعت، امنیت و پایداری</b>
<b>✅ توسعه و برنامه‌نویسی اختصاصی</b>
<b>✅ بهینه‌سازی مستمر و کاهش خطاها</b>
<b>✅ طراحی متناسب با نیاز پروژه</b>
<b>✅ خلاقیت، نوآوری و پیشرفت مداوم</b>
<b>✅ حفظ محرمانگی کدها و جزئیات فنی</b>

<b>🏅 چندین سال تجربه، در صورت تأیید سابقه تیم</b>

<b>💻 برنامه‌نویسی و توسعه توسط تیم بات اکس</b>

<b>🌟 وقتی کیفیت حرف می‌زنه، نیازی به ادعا نیست.</b>

<b>【 Licenced By 🄱🄾🅃🅇 】</b>"""

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

    await update.message.reply_html(WELCOME_TEXT.format(mention=mention))

def main():
    init_db()
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()