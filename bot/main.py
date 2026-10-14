from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
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

💥 چرا بات اکس؟

<b>✅ تمرکز بر سرعت، امنیت و پایداری</b>
<b>✅ توسعه و برنامه‌نویسی اختصاصی</b>
<b>✅ بهینه‌سازی مستمر و کاهش خطاها</b>
<b>✅ طراحی متناسب با نیاز پروژه</b>
<b>✅ خلاقیت، نوآوری و پیشرفت مداوم</b>
<b>✅ حفظ محرمانگی کدها و جزئیات فنی</b>

<b>🏅 بیش از ۷ سال تجربه، در صورت تأیید سابقه تیم</b>

💻 برنامه‌نویسی و توسعه توسط تیم بات اکس

🌟 وقتی کیفیت حرف می‌زنه، نیازی به ادعا نیست.

【 Licenced By 🄱🄾🅃🅇 】"""

ABOUT_TEXT = """ℹ️ درباره تیم بات اکس

🔱 تیم بات اکس از سال‌ها پیش در حوزه توسعه ربات‌های تلگرامی فعالیت می‌کنه و تمرکز اصلی‌ش روی ساخت سیستم‌های مدیریت گروه، ابزارهای امنیتی و قابلیت‌های اختصاصیه.

🏆 چرا تیم بات اکس؟

✅ تخصص در توسعه اختصاصی و مستقل
✅ تمرکز بر کیفیت، سرعت و پایداری
✅ به‌روزرسانی و پشتیبانی مداوم
✅ توجه به امنیت و محرمانگی اطلاعات
✅ طراحی ابزارها بر اساس نیاز واقعی کاربران
✅ چندین سال تجربه در حوزه ربات‌سازی
✅ خلاقیت و نوآوری در ارائه راهکارها

💡 اعضای تیم بات اکس همواره در تلاشن تا با بهره‌گیری از جدیدترین تکنولوژی‌ها، بهترین تجربه مدیریت گروه رو برای کاربران فارسی‌زبان فراهم کنن.

🔥 هدف ما ساختن ابزارهایی است که هم ساده و سریع باشن، هم امن و پایدار.

⚠️ اطلاعیه حقوقی و مالکیت فکری

📜 تمام کدها، طرح‌ها، ایده‌ها، قابلیت‌های اختصاصی و مستندات مربوط به پروژه‌های تیم بات اکس، متعلق به این تیم بوده و تحت حمایت قوانین مالکیت فکری و کپی‌رایت قرار داره.

🚫 هرگونه کپی‌برداری، برداشت، بازنشر یا استفاده از محتوای اختصاصی تیم بات اکس — در گروه‌ها، کانال‌ها، ربات‌ها، وب‌سایت‌ها یا هر بستر دیگه — بدون اجازه کتبی، نقض حقوق قانونی محسوب می‌شه.

⚖️ در صورت مشاهده هرگونه تخلف:
▫️ پیگیری قانونی از طریق مراجع ذی‌صلاح انجام می‌شه
▫️ از تیم یا فرد متخلف شکایت رسمی می‌شه
▫️ متخلف به‌عنوان کپی‌کار شناخته و معرفی می‌شه
▫️ اعتبار و آبروی متخلف در جامعه فنی خدشه‌دار می‌شه

🔐 تیم بات اکس به‌شدت از حقوق خودش دفاع می‌کنه و هیچ‌گونه تخلفی رو تحمل نمی‌کنه.

📌 توضیح: ایده‌های عمومی و روش‌های رایج برنامه‌نویسی به‌خودی‌خود انحصاری نیستند؛ اما آثار اختصاصی، کدها و طرح‌های اورجینال تیم بات اکس، تحت حمایت قانونی قرار دارن.

💎 تیم بات اکس؛ توسعه هدفمند، عملکرد سنجیده، پیشرفت مداوم."""


def get_main_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("➕ افزودن به گروه", url="https://t.me/BOTXAPIBOT?startgroup=true"),
        ],
        [
            InlineKeyboardButton("📢 کانال ما", url="https://t.me/BOTXTMBOT"),
            InlineKeyboardButton("👨‍💻 ارتباط با پشتیبانی", url="https://t.me/XMrAmer"),
        ],
        [
            InlineKeyboardButton("ℹ️ درباره ما", callback_data="about"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_back_keyboard():
    keyboard = [
        [InlineKeyboardButton("🔙 بازگشت", callback_data="back")]
    ]
    return InlineKeyboardMarkup(keyboard)


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

    await update.message.reply_html(
        WELCOME_TEXT.format(mention=mention),
        reply_markup=get_main_keyboard()
    )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "about":
        await query.edit_message_text(
            text=ABOUT_TEXT,
            parse_mode="HTML",
            reply_markup=get_back_keyboard()
        )
    elif query.data == "back":
        user = query.from_user
        mention = f'<a href="tg://user?id={user.id}">𓄂꯭ꪰᴀ꯭ᷧᴍ꯭ⷨᴇ꯭ⷷʀ꯭ᷢ↬𓃮™</a>'
        await query.edit_message_text(
            text=WELCOME_TEXT.format(mention=mention),
            parse_mode="HTML",
            reply_markup=get_main_keyboard()
        )


def main():
    init_db()
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    print("Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()