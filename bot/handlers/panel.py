import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from bot.utils.permissions import is_admin_or_owner

_panel_sessions = {}

def get_main_panel_keyboard():
    keyboard = [
        [InlineKeyboardButton("قفل ها", callback_data="panel_locks"), InlineKeyboardButton("لیست ها", callback_data="panel_lists")],
        [InlineKeyboardButton("تنظیمات پیشرفته", callback_data="panel_advanced"), InlineKeyboardButton("راهنما", callback_data="panel_guide")],
        [InlineKeyboardButton("بستن", callback_data="panel_close")]
    ]
    return InlineKeyboardMarkup(keyboard)

async def close_panel_after_timeout(context: ContextTypes.DEFAULT_TYPE, chat_id: int, message_id: int):
    await asyncio.sleep(180) # 3 دقیقه
    try:
        if message_id in _panel_sessions:
            await context.bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text="⋅• بدلیل عدم فعالیت پنل بصورت خودکار بسته شد !"
            )
            del _panel_sessions[message_id]
    except Exception:
        pass

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
    
    task = asyncio.create_task(close_panel_after_timeout(context, chat.id, msg.message_id))
    _panel_sessions[msg.message_id] = {
        "owner_id": update.effective_user.id,
        "timer_task": task
    }

async def panel_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    message_id = query.message.message_id
    chat_id = query.message.chat.id
    
    session = _panel_sessions.get(message_id)
    
    # اگه پنل تو دیکشنری نبود یعنی بسته شده
    if not session:
        await query.answer()
        return

    if user_id != session["owner_id"]:
        await query.answer("⋅• این پنل برای شما نیست !", show_alert=True)
        return

    # کنسل کردن تایمر قبلی (چون کاربر داره استفاده می‌کنه)
    if "timer_task" in session and not session["timer_task"].done():
        session["timer_task"].cancel()

    if query.data == "panel_close":
        await query.edit_message_text("⋅• پنل با موفقیت بسته شد !")
        del _panel_sessions[message_id]
        await query.answer()
        return
        
    await query.answer("این بخش به زودی فعال می‌شود!", show_alert=True)
    
    # ریست کردن تایمر
    task = asyncio.create_task(close_panel_after_timeout(context, chat_id, message_id))
    session["timer_task"] = task
