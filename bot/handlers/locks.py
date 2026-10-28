from telegram import Update
from telegram.ext import ContextTypes
from bot.database import get_connection
from bot.utils.permissions import is_admin_or_owner, BOT_OWNER_ID

LOCK_TYPES = {
    'گیف': 'lock_gif',
    'استیکر': 'lock_sticker',
    'عکس': 'lock_photo',
    'فیلم': 'lock_video',
    'ویدیو مسیج': 'lock_video_note',
    'رسانه': 'lock_media'
}

def is_lock_enabled(chat_id: int, lock_col: str) -> bool:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(f"SELECT {lock_col} FROM group_settings WHERE chat_id = %s", (chat_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return bool(row and row[lock_col])

def set_lock(chat_id: int, lock_col: str, enabled: bool):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(f"""
        INSERT INTO group_settings (chat_id, {lock_col})
        VALUES (%s, %s)
        ON CONFLICT (chat_id) DO UPDATE SET {lock_col} = EXCLUDED.{lock_col}
    """, (chat_id, enabled))
    conn.commit()
    cur.close()
    conn.close()

async def toggle_lock(update: Update, context: ContextTypes.DEFAULT_TYPE, lock_name: str, enable: bool):
    chat = update.effective_chat
    message = update.effective_message

    if chat.type == "private" or not await is_admin_or_owner(update, context):
        return

    lock_col = LOCK_TYPES[lock_name]
    is_currently_locked = is_lock_enabled(chat.id, lock_col)

    if enable:
        if is_currently_locked:
            await message.reply_text(f"⋅• قفل {lock_name} در حال حاضر فعال است !")
            return
        set_lock(chat.id, lock_col, True)
        await message.reply_text(f"⋅• قفل {lock_name} با موفقیت فعال شد !")
    else:
        if not is_currently_locked:
            await message.reply_text(f"⋅• قفل {lock_name} در حال حاضر غیرفعال است !")
            return
        set_lock(chat.id, lock_col, False)
        await message.reply_text(f"•⋅ قفل {lock_name} با موفقیت غیرفعال شد !")

# توابع اختصاصی برای هندلرها
async def lock_gif(update: Update, context: ContextTypes.DEFAULT_TYPE): await toggle_lock(update, context, 'گیف', True)
async def unlock_gif(update: Update, context: ContextTypes.DEFAULT_TYPE): await toggle_lock(update, context, 'گیف', False)

async def lock_sticker(update: Update, context: ContextTypes.DEFAULT_TYPE): await toggle_lock(update, context, 'استیکر', True)
async def unlock_sticker(update: Update, context: ContextTypes.DEFAULT_TYPE): await toggle_lock(update, context, 'استیکر', False)

async def lock_photo(update: Update, context: ContextTypes.DEFAULT_TYPE): await toggle_lock(update, context, 'عکس', True)
async def unlock_photo(update: Update, context: ContextTypes.DEFAULT_TYPE): await toggle_lock(update, context, 'عکس', False)

async def lock_video(update: Update, context: ContextTypes.DEFAULT_TYPE): await toggle_lock(update, context, 'فیلم', True)
async def unlock_video(update: Update, context: ContextTypes.DEFAULT_TYPE): await toggle_lock(update, context, 'فیلم', False)

async def lock_video_note(update: Update, context: ContextTypes.DEFAULT_TYPE): await toggle_lock(update, context, 'ویدیو مسیج', True)
async def unlock_video_note(update: Update, context: ContextTypes.DEFAULT_TYPE): await toggle_lock(update, context, 'ویدیو مسیج', False)

async def lock_media(update: Update, context: ContextTypes.DEFAULT_TYPE): await toggle_lock(update, context, 'رسانه', True)
async def unlock_media(update: Update, context: ContextTypes.DEFAULT_TYPE): await toggle_lock(update, context, 'رسانه', False)

# محافظ رسانه‌ها
async def media_guard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message
    chat = update.effective_chat
    user = update.effective_user

    if chat.type == "private" or not message or not user:
        return
    if user.id == BOT_OWNER_ID:
        return
        
    try:
        member = await context.bot.get_chat_member(chat.id, user.id)
        if member.status in ("administrator", "creator"):
            return
    except Exception:
        pass

    # چک کردن اینکه آیا این نوع پیام قفل هست یا نه
    is_locked = False
    if (message.animation or message.document) and is_lock_enabled(chat.id, 'lock_gif'):
        is_locked = True
    elif message.sticker and is_lock_enabled(chat.id, 'lock_sticker'):
        is_locked = True
    elif message.photo and is_lock_enabled(chat.id, 'lock_photo'):
        is_locked = True
    elif message.video and is_lock_enabled(chat.id, 'lock_video'):
        is_locked = True
    elif message.video_note and is_lock_enabled(chat.id, 'lock_video_note'):
        is_locked = True
        
    # قفل رسانه کلی
    if is_lock_enabled(chat.id, 'lock_media'):
        if message.photo or message.video or message.animation or message.sticker or message.video_note or message.voice or message.audio or message.document:
            is_locked = True

    if is_locked:
        try:
            await message.delete()
        except Exception:
            return

        # هشدار مشابه قفل لینک
        mention = user.mention_html()
        warn_text = (
            f"⫸ کاربر گرامی : {mention} ⚠\n"
            f"⌫ ارسال این نوع رسانه در گروه ممنوع می‌باشد به همین دلیل پیام شما پاک شد !\n"
            f"◂ لطفاً از ارسال آن خودداری فرمایید.\n"
            f"⋆ با تشکر از همکاری شما."
        )
        try:
            warn = await context.bot.send_message(chat_id=chat.id, text=warn_text, parse_mode="HTML")
            import asyncio
            asyncio.create_task(delete_later(context, chat.id, warn.message_id, 10))
        except Exception:
            pass

async def delete_later(context, chat_id, message_id, seconds):
    import asyncio
    await asyncio.sleep(seconds)
    try:
        await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
    except Exception:
        pass
