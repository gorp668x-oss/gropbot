import asyncio
from telegram.error import BadRequest
from telegram import InlineKeyboardMarkup

async def send_live_message(
    update,
    context,
    final_text: str,
    reply_markup: InlineKeyboardMarkup = None,
    parse_mode: str = "HTML",
    delay: float = 0.015
):
    """
    پیام را با تقسیم‌بندی خط به خط و سرعت بالا ارسال می‌کند.
    """
    try:
        msg = await update.message.reply_text(".", parse_mode=parse_mode)
    except Exception as e:
        print(f"[live_message] Failed to send initial message: {e}")
        return None

    # تقسیم متن به خطوط
    lines = final_text.split('\n')
    current_text = ""
    
    for line in lines:
        if current_text:
            current_text += "\n" + line
        else:
            current_text = line
            
        # اگر خط خالی بود یا اینکه متن هنوز طولانی نشده، مستقیم اضافه کن
        if not line.strip():
            continue

        try:
            await msg.edit_text(current_text, parse_mode=parse_mode)
        except BadRequest as e:
            if "not modified" not in str(e).lower():
                pass
        except Exception:
            pass
            
        await asyncio.sleep(delay)

    # پیام نهایی همراه با دکمه‌ها
    try:
        await msg.edit_text(final_text, parse_mode=parse_mode, reply_markup=reply_markup)
    except BadRequest as e:
        if "not modified" not in str(e).lower():
            try:
                await update.message.reply_text(final_text, parse_mode=parse_mode, reply_markup=reply_markup)
            except Exception:
                pass
    except Exception:
        pass

    return msg
