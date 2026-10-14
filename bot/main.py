from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from bot.config import TELEGRAM_TOKEN
from bot.database import init_db, get_connection

WELCOME_TEXT = """🔱 سلام {mention} 🌹

🗣️ من <b>بات اکس</b> هستم؛ فراتر از یک ربات، یک سیستم قدرتمند برای مدیریت هوشمند گروه‌ها!

🚀 تفاوت ما با دیگران فقط در حرف نیست؛ در عملکرد ماست!

⚙️ امکانات و قابلیت‌های بات اکس:

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
⚡️ سرعت بالا و عملکرد بهینه
🖥 زیرساخت اختصاصی
🔬 امکان تست پیش از انتخاب

💥 <b>چرا بات اکس؟</b>

✅ تمرکز بر سرعت، امنیت و پایداری
✅ توسعه و برنامه‌نویسی اختصاصی
✅ بهینه‌سازی مستمر و کاهش خطاها
✅ طراحی متناسب با نیاز پروژه
✅ خلاقیت، نوآوری و پیشرفت مداوم
✅ حفظ محرمانگی کدها و جزئیات فنی

🏅 چندین سال تجربه، در صورت تأیید سابقه تیم

💻 برنامه‌نویسی و توسعه توسط تیم بات اکس

🌟 وقتی کیفیت حرف می‌زنه، نیازی به ادعا نیست.

【 Licenced By 🄱🄾🅃🅇 】"""

ABOUT_TEXT = """ℹ️ درباره بات اکس

🔱 بات اکس یک سیستم مدیریت گروه حرفه‌ای و پیشرفته است که توسط تیم بات اکس توسعه داده شده.

🏆 چرا تیم بات اکس از همه بهتره؟

✅ بدون باگ و پایدار
✅ سرعت بالا و عملکرد بهینه
✅ پشتیبانی مداوم و به‌روزرسانی
✅ توسعه اختصاصی و مستقل
✅ تمرکز بر امنیت و محرمانگی
✅ چندین سال تجربه در این حوزه
✅ طراحی متناسب با نیاز واقعی پروژه

💡 تیم بات اکس همواره در تلاشه که بهترین کیفیت، بالاترین سرعت و بیشترین امکانات رو در اختیار کاربران قرار بده.

🔥 هدف ما: ارائه یک ربات بی‌نقص، بدون باگ و پایدار برای مدیریت آسان گروه‌ها.

⚠️ اطلاعیه حقوقی و مالکیت فکری

📜 تمام کدها، طرح‌ها، ایده‌ها، قابلیت‌های اختصاصی و مستندات مربوط به بات اکس، متعلق به تیم بات اکس است و تحت حمایت قوانین مالکیت فکری و کپی‌رایت قرار داره.

🚫 هرگونه کپی‌برداری، برداشت، بازنشر یا استفاده از محتوای اختصاصی تیم بات اکس — در گروه‌ها، کانال‌ها، ربات‌ها، وب‌سایت‌ها یا هر بستر دیگه — بدون اجازه کتبی، نقض حقوق قانونی محسوب می‌شه.

⚖️ در صورت مشاهده هرگونه تخلف:
▫️ پیگیری قانونی از طریق مراجع ذی‌صلاح انجام می‌شه
▫️ از تیم متخلف شکایت رسمی می‌شه
▫️ تیم متخلف به‌عنوان کپی‌کار شناخته و معرفی می‌شه
▫️ اعتبار و آبروی تیم متخلف در جامعه فنی خدشه‌دار می‌شه

🔐 تیم بات اکس به‌شدت از حقوق خودش دفاع می‌کنه و هیچ‌گونه تخلفی رو تحمل نمی‌کنه.

📌 توضیح: ایده‌های عمومی و روش‌های رایج برنامه‌نویسی به‌خودی‌خود انحصاری نیستند؛ اما آثار اختصاصی، کدها و طرح‌های اورجینال تیم بات اکس، تحت حمایت قانونی قرار دارن.

💎 بات اکس؛ توسعه هدفمند، عملکرد سنجیده، پیشرفت مداوم."""


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