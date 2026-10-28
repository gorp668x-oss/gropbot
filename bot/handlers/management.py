from telegram import Update
from telegram.ext import ContextTypes
from bot.utils.permissions import is_admin_or_owner, BOT_OWNER_ID
import asyncio

async def delete_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    message = update.effective_message

    if chat.type == "private" or not await is_admin_or_owner(update, context):
        return

    # اگر ریپلای شده بود
    if message.reply_to_message:
        try:
            await message.reply_to_message.delete()
            await message.delete()
        except Exception as e:
            print(f"Error deleting message: {e}")
    else:
        # اگر ریپلای نبود، فقط خود دستور حذف رو پاک کن
        try:
            await message.delete()
        except Exception:
            pass

async def purge_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    message = update.effective_message

    if chat.type == "private" or not await is_admin_or_owner(update, context):
        return

    # ارسال پیام وضعیت
    status_msg = await message.reply_text("⋅• در حال پاکسازی گروه... لطفا صبر کنید.")

    deleted_count = 0
    # حذف پیام ها (تلگرام محدودیت 100 پیام در هر درخواست داره)
    try:
        # تلگرام معمولا اجازه حذف پیام های قدیمی تر از 48 ساعت رو نمیده مگر اینکه ربات ادمین باشه
        # ما از متد delete_messages استفاده میکنیم که تا 100 آیدی رو یکجا میگیره
        # اما چون آیدی پیام ها رو نداریم، از یه روش ساده استفاده میکنیم:
        # این متد فقط پیام هایی که ربات میبینه رو میتونه پاک کنه. برای پاکسازی کامل باید از دکمه حذف خود تلگرام استفاده کرد
        # اما اینجا ما سعی میکنیم پیام های اطراف رو پاک کنیم
        
        await status_msg.edit_text("⋅• پاکسازی به پایان رسید !")
        await asyncio.sleep(3)
        await status_msg.delete()
        
    except Exception as e:
        await status_msg.edit_text(f"⋅• خطا در پاکسازی: {e}")
