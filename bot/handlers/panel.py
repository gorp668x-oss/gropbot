from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from bot.utils.permissions import is_admin_or_owner

def get_main_panel_keyboard():
    keyboard = [
        [InlineKeyboardButton("⚙️ تنظیمات پیشرفته", callback_data="panel_advanced"), InlineKeyboardButton("📊 لیست ها", callback_data="panel_lists")],
        [InlineKeyboardButton("🔐 قفل ها", callback_data="panel_locks"), InlineKeyboardButton("📖 راهنما", callback_data="panel_guide")],
        [InlineKeyboardButton("❌ بستن", callback_data="panel_close")]
    ]
    return InlineKeyboardMarkup(keyboard)

async def panel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    if chat.type == "private":
        return
    if not await is_admin_or_owner(update, context):
        return

    await update.message.reply_text(
        "👤 <b>مدیر</b>

"
        "لطفا بخش مورد نظر را انتخاب کنید :",
        parse_mode="HTML",
        reply_markup=get_main_panel_keyboard()
    )

# این تابع برای هندل کردن کلیک روی دکمه های پنل فعلا فقط یه پیام میده که کار نمیکنه
async def panel_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer("این بخش به زودی فعال می‌شود!", show_alert=True)
