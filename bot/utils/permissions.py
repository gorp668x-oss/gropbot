from telegram import Update
from telegram.ext import ContextTypes

BOT_OWNER_ID = 7803165903


async def is_admin_or_owner(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """بررسی دسترسی: مالک گروه، ادمین‌ها و سازنده ربات"""
    user = update.effective_user
    chat = update.effective_chat

    if user is None or chat is None:
        return False

    # سازنده ربات
    if user.id == BOT_OWNER_ID:
        return True

    # توی پیوی نمی‌شه ادمین گروه بود
    if chat.type == "private":
        return False

    # بررسی ادمین بودن
    try:
        member = await context.bot.get_chat_member(chat.id, user.id)
        if member.status in ("administrator", "creator"):
            return True
    except Exception:
        pass

    return False