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

ABOUT_TEXT = """ℹ️ <b>درباره تیم بات اکس</b>

🔱 تیم بات اکس سال‌هاست در حوزه <b>توسعه ربات‌های تلگرامی</b> و <b>سیستم‌های مدیریت گروه</b> فعالیت می‌کنه.

🏆 <b>چرا تیم بات اکس؟</b>

✅ <b>توسعه اختصاصی و مستقل</b>
✅ تمرکز بر <b>کیفیت، سرعت و پایداری</b>
✅ <b>امنیت و محرمانگی</b> اطلاعات
✅ پشتیبانی و به‌روزرسانی مداوم
✅ تجربه چندین ساله در ربات‌سازی
✅ <b>خلاقیت و نوآوری</b> در راهکارها

🔥 <b>هدف ما:</b> ساخت ابزارهایی ساده، سریع، امن و پایدار برای مدیریت گروه‌ها.

⚠️ <b>اطلاعیه حقوقی و مالکیت فکری</b>

📜 کدها، طرح‌ها و ایده‌های اختصاصی تیم بات اکس، تحت حمایت <b>قوانین مالکیت فکری و کپی‌رایت</b> قرار داره.

🚫 هرگونه کپی‌برداری یا استفاده از محتوای اختصاصی ما — در گروه‌ها، کانال‌ها، ربات‌ها، سایت‌ها یا هر بستر دیگه — بدون اجازه کتبی، <b>نقض حقوق قانونی</b> محسوب می‌شه.

⚖️ <b>در صورت تخلف:</b>
▫️ پیگیری قانونی انجام می‌شه
▫️ شکایت رسمی ثبت می‌شه
▫️ متخلف به‌عنوان <b>کپی‌کار</b> شناخته و معرفی می‌شه

🔐 تیم بات اکس قویاً از <b>حقوق خودش</b> دفاع می‌کنه.

💎 <b>تیم بات اکس؛ توسعه هدفمند، عملکرد سنجیده.</b>"""

MORE_INFO_TEXT = """➕ <b>اطلاعات تکمیلی درباره بات اکس</b>

✅ بات اکس روی <b>سرورهای اختصاصی آمستردام هلند</b> اجرا می‌شه که کمترین پینگ رو به تلگرام دارن؛ نتیجه‌ش <b>سرعت بالاتر</b> در دریافت و پردازش اطلاعاته.

✅ هدف ما <b>حفاظت کامل از گروه شماست</b>. هیچ تبلیغی توی گروهت ارسال نمی‌شه و مثل خیلی از ربات‌های دیگه از این راه درآمد کسب نمی‌کنیم؛ چون معتقدیم <b>ارزش گروه شما بالاتر از این حرفاست</b>.

✅ <b>هیچ سوءاستفاده‌ای</b> از گروهت انجام نمی‌شه و می‌تونی با خیال راحت به ما اعتماد کنی.

✅ تمام <b>قابلیت‌های کاربردی</b> مورد نیاز برای اکثر سبک‌های گروهی توی ربات قرار گرفته. اگه قابلیت خاصی درخواست کنی، <b>در سریع‌ترین زمان</b> اضافه می‌شه.

✅ ربات همیشه در حال <b>آپدیت و پیشرفت</b>ه و تلاش می‌کنه کار مشتری‌هاش رو ساده‌تر و ساده‌تر کنه.

✅ سیستم <b>پاکسازی پیام‌ها</b> خیلی پیشرفته طراحی شده؛ می‌تونه تمام پیام‌ها رو تا اولین روز تأسیس گروه، در کمتر از <b>۳ ثانیه</b> حذف کنه.

✅ سیستم <b>شناسایی تبچی</b> و ربات‌های مخرب با کمترین درصد خطا کار می‌کنه و می‌تونه ربات‌های مخرب رو محدود یا اخراج کنه.

✅ <b>مشتری توی دیدگاه ما بالاترین مقام رو داره</b>؛ هیچ‌وقت در مواجهه با مشکل تنها نمی‌مونی و همیشه پشتت هستیم.

✅ تمامی فعالیت‌ها <b>زیر نظر و ثبت</b> قرار می‌گیره و هر زمان بتونی <b>آمار کلی فعالیت‌های گروه</b> رو دریافت کنی.

✅ دستورات <b>دو زبانه (فارسی و انگلیسی)</b> هستن و <b>پنل شیشه‌ای</b> داره که با اون می‌تونی همه تنظیمات گروه رو مدیریت کنی.

✅ این ربات توسط <b>یک تیم حرفه‌ای و با تجربه</b> برنامه‌نویسی شده و هدف اصلیش <b>ایجاد امنیت و سهولت مدیریت</b> در گروهته. از هیچ نظری از بقیه ربات‌ها عقب‌تر نیست و <b>چندین قدم جلوتره</b>.

💬 <b>جهت مشاوره و نصب:</b>
🆔 @XMrAmer"""


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
            InlineKeyboardButton("➕ اطلاعات بیشتر", callback_data="more_info"),
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
    elif query.data == "more_info":
        await query.edit_message_text(
            text=MORE_INFO_TEXT,
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