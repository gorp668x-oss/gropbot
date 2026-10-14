from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes
)
from bot.config import TELEGRAM_TOKEN
from bot.database import init_db, get_connection

WELCOME_TEXT = """🔱 سلام {mention} 🌹

🗣️ من فراتر از یک ربات مدیریت گروه هستم؛ یک <b>سیستم هوشمند و قدرتمند</b> برای کنترل کامل گروه‌های تلگرامی!

🚀 تفاوت من با دیگران فقط در حرف نیست؛ در عملکرد ثابت می‌شه!

⚙️ امکانات و قابلیت‌ها:

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

💥 چرا من؟

<b>✅ تمرکز بر سرعت، امنیت و پایداری</b>
<b>✅ توسعه و برنامه‌نویسی اختصاصی</b>
<b>✅ بهینه‌سازی مستمر و کاهش خطاها</b>
<b>✅ طراحی متناسب با نیاز پروژه</b>
<b>✅ خلاقیت، نوآوری و پیشرفت مداوم</b>
<b>✅ حفظ محرمانگی کدها و جزئیات فنی</b>

<b>🏅 بیش از ۷ سال تجربه تیم پشتیبان</b>

💻 برنامه‌نویسی و توسعه توسط تیم بات اکس

🌟 وقتی کیفیت حرف می‌زنه، نیازی به ادعا نیست.

【 Licenced By 🄱🄾🅃🅇 】"""

ABOUT_TEXT = """ℹ️ <b>درباره تیم بات اکس</b>

تیم بات اکس یک مجموعه حرفه‌ای است که با هدف <b>ایجاد امنیت، سرعت و سهولت</b> در مدیریت گروه‌های تلگرامی، سیستم بات اکس را طراحی و توسعه داده است.

🏆 <b>مزیت‌های تیم بات اکس</b>

✅ <b>توسعه اختصاصی و مستقل</b> بدون وابستگی به پلتفرم‌های آماده
✅ تمرکز جدی بر <b>کیفیت، سرعت و پایداری</b> در طراحی
✅ رعایت <b>اصول امنیتی و محرمانگی</b> اطلاعات کاربران
✅ پشتیبانی و به‌روزرسانی مداوم
✅ تجربه چندین ساله در حوزه ربات‌سازی
✅ <b>خلاقیت و نوآوری</b> در ارائه راهکارهای فنی

🔥 <b>هدف ما</b> ارائه ابزارهایی ساده، سریع، امن و پایدار برای مدیریت آسان گروه‌های تلگرامی است.

⚠️ <b>اطلاعیه مالکیت فکری</b>

📜 کلیه کدها، طرح‌ها، ایده‌ها و مستندات اختصاصی تیم بات اکس، تحت حمایت <b>قوانین مالکیت فکری و کپی‌رایت</b> قرار دارد.

🚫 هرگونه کپی‌برداری یا استفاده از محتوای اختصاصی، در گروه‌ها، کانال‌ها، ربات‌ها، وب‌سایت‌ها یا هر بستر دیگر — بدون کسب اجازه کتبی — <b>نقض حقوق قانونی</b> محسوب می‌شود.

⚖️ <b>در صورت مشاهده هرگونه تخلف</b>
▫️ پیگیری قانونی از طریق مراجع ذی‌صلاح انجام خواهد شد
▫️ شکایت رسمی ثبت می‌گردد
▫️ متخلف به‌عنوان <b>کپی‌کار</b> معرفی خواهد شد

🔐 تیم بات اکس با جدیت از <b>حقوق قانونی خود</b> دفاع می‌کند.

💎 <b>تیم بات اکس؛ توسعه هدفمند، عملکرد سنجیده، پیشرفت مداوم.</b>"""

MORE_INFO_TEXT = """➕ <b>اطلاعات تکمیلی درباره تیم بات اکس</b>

🔹 زیرساخت تیم بات اکس بر پایه <b>سرورهای اختصاصی آمستردام هلند</b> بنا شده است. این سرورها کمترین پینگ را نسبت به تلگرام دارند و همین موضوع باعث <b>سرعت بالاتر</b> در دریافت و پردازش اطلاعات گروه می‌شود.

🔹 هدف اصلی تیم بات اکس، <b>حفاظت همه‌جانبه از گروه شما</b> است. هیچ‌گونه تبلیغاتی در گروه ارسال نمی‌شود و برخلاف بسیاری از ربات‌های مشابه، از این طریق کسب درآمد نمی‌کنیم؛ چرا که معتقدیم <b>ارزش گروه شما بالاتر از این موضوعات</b> است.

🔹 <b>هیچ‌گونه سوءاستفاده‌ای</b> از گروه شما توسط تیم بات اکس انجام نمی‌شود و می‌توانید با اطمینان کامل به ما اعتماد کنید.

🔹 تمامی <b>قابلیت‌های کاربردی</b> مورد نیاز اکثر سبک‌های گروهی در تیم بات اکس در نظر گرفته شده است. در صورت درخواست قابلیت جدید، آن قابلیت <b>در سریع‌ترین زمان ممکن</b> به ربات اضافه می‌شود.

🔹 تیم بات اکس همواره در حال <b>به‌روزرسانی و پیشرفت</b> است و تلاش می‌کند بهترین خدمات را در اختیار کاربران قرار دهد.

🔹 سیستم <b>پاک‌سازی پیام‌ها</b> در تیم بات اکس بسیار پیشرفته طراحی شده و قادر است تمامی پیام‌ها را تا نخستین روز تأسیس گروه، در کمتر از <b>۳ ثانیه</b> حذف کند.

🔹 سیستم <b>شناسایی تبچی و ربات‌های مخرب</b> با کمترین درصد خطا عمل می‌کند و می‌تواند ربات‌های مخرب را محدود یا اخراج نماید.

🔹 <b>جایگاه مشتری</b> در دیدگاه تیم بات اکس بسیار بالاست. هیچ‌گاه شما را در مواجهه با مشکلات و پرسش‌ها تنها نمی‌گذاریم و همواره پشتیبان شما خواهیم بود.

🔹 تمامی فعالیت‌ها <b>ثبت و پایش</b> می‌شود و می‌توانید در هر زمان <b>آمار کلی فعالیت‌های گروه</b> را دریافت کنید.

🔹 دستورات ربات به‌صورت <b>دوزبانه (فارسی و انگلیسی)</b> طراحی شده و ساختاری ساده دارد تا استفاده از آن برای همه راحت باشد. همچنین یک <b>پنل شیشه‌ای</b> در اختیار شماست که با آن می‌توانید تمام تنظیمات گروه را مدیریت کنید.

🔹 تیم بات اکس توسط <b>یک تیم حرفه‌ای و باتجربه</b> برنامه‌نویسی شده و هدف اصلی آن <b>ایجاد امنیت و سهولت مدیریت</b> در گروه شماست. از هیچ نظری از سایر ربات‌ها عقب‌تر نیست و در بسیاری از بخش‌ها <b>چندین قدم جلوتر</b> است.

💻 <b>جهت مشاوره و نصب:</b>
👨‍💻 @XMrAmer"""

DIFF_TEXT = """🆚 <b>تفاوت نسخه رایگان و اشتراکی</b>

در تیم بات اکس، دو نسخه برای استفاده وجود داره: <b>رایگان</b> و <b>اشتراکی (ویژه)</b>. هر کدوم برای نیازهای متفاوتی طراحی شدن.

🆓 <b>نسخه رایگان</b>

مناسب برای گروه‌های کوچک و تازه تأسیس.
🔹 قابلیت‌های پایه مدیریت گروه
🔹 ضد لینک و ضد فحش ساده
🔹 خوش‌آمدگویی ابتدایی
🔹 آمار محدود کاربران
🔹 پشتیبانی از طریق گروه
🔹 محدودیت در تعداد قفل‌ها
🔹 سرعت پایه (سرور مشترک)

💎 <b>نسخه اشتراکی (ویژه)</b>

مناسب برای گروه‌های فعال، بزرگ و حرفه‌ای.
🔸 <b>تمام قابلیت‌های نسخه رایگان</b>
🔸 سیستم <b>هوش مصنوعی (AI)</b> فعال
🔸 سیستم <b>TIG ضد ممبر دزد</b>
🔸 سیستم <b>ABM ضد خیانت</b>
🔸 <b>درآمدزایی از گروه</b>
🔸 شناسایی رسانه‌های +18
🔸 سامانه تشخیص تبچی
🔸 انواع قفل‌های پیشرفته
🔸 اد و کانال اجباری
🔸 آمار روزانه و ماهانه کامل
🔸 <b>پنل شیشه‌ای اختصاصی</b>
🔸 <b>سرور اختصاصی پرسرعت</b>
🔸 پشتیبانی مستقیم و اختصاصی
🔸 درخواست قابلیت جدید
🔸 دوزبانه (فارسی و انگلیسی)

🎯 <b>کدوم رو انتخاب کنم؟</b>

🔹 اگه یه گروه کوچیک داری و فقط قابلیت‌های پایه رو می‌خوای → <b>نسخه رایگان</b>
🔹 اگه یه گروه بزرگ، فعال یا حرفه‌ای داری و امنیت و امکانات کامل برات مهمه → <b>نسخه اشتراکی</b>

💻 <b>جهت دریافت نسخه اشتراکی یا مشاوره:</b>
👨‍💻 @XMrAmer"""

UNKNOWN_REPLY = """💥 متأسفانه متوجه منظور شما نشدم.

✅ برای دریافت متن استارت، دستور /start را ارسال نمایید.

👨‍💻 برای ارتباط با پشتیبانی: @XMrAmer"""


def get_main_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("📓 اطلاعات بیشتر", callback_data="more_info"),
        ],
        [
            InlineKeyboardButton("📢 کانال ربات", url="https://t.me/BOTXTMBOT"),
            InlineKeyboardButton("💬 گروه پشتیبانی", url="https://t.me/GPBOTXTMBOT"),
        ],
        [
            InlineKeyboardButton("🆚 تفاوت رایگان و اشتراکی", callback_data="diff"),
        ],
        [
            InlineKeyboardButton("👨‍💻 پشتیبانی", url="https://t.me/XMrAmer"),
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


async def unknown_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        UNKNOWN_REPLY,
        disable_web_page_preview=True
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
    elif query.data == "diff":
        await query.edit_message_text(
            text=DIFF_TEXT,
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
    app.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND & filters.ChatType.PRIVATE,
        unknown_message
    ))

    print("Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()
