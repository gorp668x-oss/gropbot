import asyncio
from telegram.error import BadRequest
from telegram import InlineKeyboardMarkup

async def send_live_message(
    update,
    context,
    final_text: str,
    reply_markup: InlineKeyboardMarkup = None,
    parse_mode: str = "HTML",
    steps: int = 10,       # کاهش تعداد مراحل به 10
    delay: float = 0.01    # کاهش تاخیر به 0.01 ثانیه
):
    try:
        msg = await update.message.reply_text(".", parse_mode=parse_mode)
    except Exception as e:
        print(f"[live_message] Failed to send initial message: {e}")
        return None

    total_len = len(final_text)
    if total_len == 0:
        return msg

    # محاسبه اندازه هر بلوک برای رسیدن به تعداد مراحل مشخص
    step_size = max(1, total_len // steps)
    
    current = ""
    i = step_size
    while i < total_len:
        chunk = final_text[:i]
        if chunk != current:
            try:
                await msg.edit_text(chunk, parse_mode=parse_mode)
                current = chunk
            except BadRequest as e:
                if "not modified" not in str(e).lower():
                    pass
            except Exception:
                pass
        await asyncio.sleep(delay)
        i += step_size

    # پیام نهایی
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
