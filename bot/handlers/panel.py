from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from bot.utils.permissions import is_admin_or_owner

def get_main_panel_keyboard():
    keyboard = [
        [InlineKeyboardButton("قفل ها", callback_data="panel_locks"), InlineKeyboardButton("لیست ها", callback_data="panel_lists")],
        [InlineKeyboardButton("تنظیمات پیشرفته", callback_data="panel_advanced"), InlineKeyboardButton("راهنما", callback_data="panel_guide")],
        [InlineKeyboardButton("بستن", callback_data="panel_close")]
    ]
    return InlineKeyboardMarkup(keyboard)

async def panel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    if chat.type == "private":
        return
    if not await is_admin_or_owner(update, context):
        return

    # دقیقا مثل متن خواسته شده
    text = "⋅• بخش مورد نظر را انتخاب کنید :\n──┅═✾ صفحه اصلی ✾═┅──"
    
    await update.message.reply_text(
        text,
        reply_markup=get_main_panel_keyboard()
    )

async def panel_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query.data == "panel_close":
        await query.message.delete()
        await query.answer()
        return
        
    await query.answer("این بخش به زودی فعال می‌شود!", show_alert=True)
