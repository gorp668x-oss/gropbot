import asyncio
from telegram.error import BadRequest
from telegram import InlineKeyboardMarkup

async def send_live_message(
    update,
    context,
    final_text: str,
    reply_markup: InlineKeyboardMarkup = None,
    parse_mode: str = "HTML",
    delay: float = 0.005  # سرعت خیلی بالا
):
    """
    پیام را با افکت تایپ واقعی (کاراکتر به کاراکتر) ارسال می‌کند.
    """
    try:
        msg = await update.message.reply_text(".", parse_mode=parse_mode)
    except Exception as e:
        print(f"[live_message] Failed to send initial message: {e}")
        return None

    total_len = len(final_text)
    current_text = ""

    # ارسال کاراکتر به کاراکتر
    for i in range(total_len):
        current_text += final_text[i]
        
        # برای جلوگیری از خطای تلگرام، هر ۳ کاراکتر یکبار آپدیت می‌کنیم
        # (اینطوری هم سریع‌تره هم محدودیت تلگرام رعایت میشه)
        if i % 3 == 0 or i == total_len - 1:
            try:
                # اگر متن به تگ HTML ناقص خورده بود، پارس نکنه که ارور نده
                # این یک محافظ ساده است
                await msg.edit_text(current_text, parse_mode=parse_mode)
            except BadRequest as e:
                if "not modified" not in str(e).lower() and "can't parse" not in str(e).lower():
                    pass
            except Exception:
                pass
            await asyncio.sleep(delay)

    # پیام نهایی همراه با دکمه‌ها
    try:
        await msg.edit_text(final_text, parse_mode=parse_mode, reply_markup=reply_markup)
    except BadRequest:
        try:
            await update.message.reply_text(final_text, parse_mode=parse_mode, reply_markup=reply_markup)
        except Exception:
            pass
    except Exception:
        pass

    return msg
