from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from bot.utils.permissions import is_admin_or_owner

# دیکشنری برای ذخیره اینکه پنل متعلق به کیست
# فرمت: {message_id: user_id}
_panel_owners = {}

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

    text = "⋅• بخش مورد نظر را انتخاب کنید :\n──┅═✾ صفحه اصلی ✾═┅──"
    
    msg = await update.message.reply_text(
        text,
        reply_markup=get_main_panel_keyboard()
    )
    # ذخیره آیدی کسی که پنل رو باز کرده
    _panel_owners[msg.message_id] = update.effective_user.id

async def panel_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    message_id = query.message.message_id
    
    # چک کردن اینکه آیا این کاربر همون کسی هست که پنل رو باز کرده
    owner_id = _panel_owners.get(message_id)
    
    if owner_id and user_id != owner_id:
        await query.answer("⋅• این پنل برای شما نیست !", show_alert=True)
        return

    if query.data == "panel_close":
        await query.message.delete()
        if message_id in _panel_owners:
            del _panel_owners[message_id]
        await query.answer()
        return
        
    await query.answer("این بخش به زودی فعال می‌شود!", show_alert=True)
