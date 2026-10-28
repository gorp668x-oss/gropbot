from telegram import Update
from telegram.ext import ContextTypes
from bot.database import get_connection
from bot.utils.permissions import is_admin_or_owner, BOT_OWNER_ID
import asyncio

LOCK_TYPES = {
    'گیف': 'lock_gif',
    'استیکر': 'lock_sticker',
    'عکس': 'lock_photo',
    'فیلم': 'lock_video',
    'ویدیو مسیج': 'lock_video_note',
    'رسانه': 'lock_media',
    'ویس': 'lock_voice',
    'پورن': 'lock_porn',
    'آیدی': 'lock_id',
    'تبچی': 'lock_tabchi',
    'گروه': 'lock_group'
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

async def delete_later(context, chat_id, message_id, seconds):
    await asyncio.sleep(seconds)
    try:
        await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
    except Exception:
        pass

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

    media_name = None
    
    if message.animation:
        if is_lock_enabled(chat.id, 'lock_gif') or is_lock_enabled(chat.id, 'lock_media'):
            media_name = "گیف"
    elif message.sticker:
        if is_lock_enabled(chat.id, 'lock_sticker') or is_lock_enabled(chat.id, 'lock_media'):
            media_name = "استیکر"
    elif message.photo:
        if is_lock_enabled(chat.id, 'lock_photo') or is_lock_enabled(chat.id, 'lock_media'):
            media_name = "عکس"
    elif message.video:
        if is_lock_enabled(chat.id, 'lock_video') or is_lock_enabled(chat.id, 'lock_media'):
            media_name = "فیلم"
    elif message.video_note:
        if is_lock_enabled(chat.id, 'lock_video_note') or is_lock_enabled(chat.id, 'lock_media'):
            media_name = "ویدیو مسیج"
    elif message.voice:
        if is_lock_enabled(chat.id, 'lock_voice') or is_lock_enabled(chat.id, 'lock_media'):
            media_name = "ویس"
    elif message.audio or message.document:
        if is_lock_enabled(chat.id, 'lock_media'):
            media_name = "رسانه"

    # بررسی متنی برای قفل‌های خاص
    text = (message.text or message.caption or "").lower()
    
    if text:
        if is_lock_enabled(chat.id, 'lock_id') and ('@' in text or 't.me/' in text or 'telegram.me/' in text):
            media_name = "آیدی/لینک"
        elif is_lock_enabled(chat.id, 'lock_group') and ('t.me/' in text or 'telegram.me/' in text or 'joinchat' in text):
            media_name = "لینک گروه"
        elif is_lock_enabled(chat.id, 'lock_porn') and any(word in text for word in ['پورن', 'سکس', '18+', 'xxx', 'porn']):
            media_name = "محتوای غیراخلاقی"
        elif is_lock_enabled(chat.id, 'lock_tabchi') and ('تبچی' in text or 'تب چی' in text):
            media_name = "تبلیغات"

    if media_name:
        try:
            await message.delete()
        except Exception:
            return

        mention = user.mention_html()
        warn_text = (
            f"⫸ کاربر گرامی : {mention} ⚠\n"
            f"⌫ ارسال {media_name} در گروه ممنوع می‌باشد به همین دلیل پیام شما حذف شد !\n"
            f"⋆ با تشکر از همکاری شما."
        )
        try:
            warn = await context.bot.send_message(chat_id=chat.id, text=warn_text, parse_mode="HTML")
            asyncio.create_task(delete_later(context, chat.id, warn.message_id, 15))
        except Exception:
            pass
