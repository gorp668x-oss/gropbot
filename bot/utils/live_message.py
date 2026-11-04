import asyncio
import logging
from telegram.error import BadRequest, RetryAfter
from telegram import InlineKeyboardMarkup

logger = logging.getLogger(__name__)

async def send_live_message(
    bot,
    chat_id: int,
    final_text: str,
    reply_markup: InlineKeyboardMarkup = None,
    parse_mode: str = "HTML",
    delay: float = 0.02,
    reply_to_message_id: int = None,
):
    try:
        msg = await bot.send_message(
            chat_id=chat_id, 
            text=".", 
            reply_to_message_id=reply_to_message_id
        )
    except Exception as e:
        logger.exception(f"Could not send initial message: {e}")
        return None

    # جدا کردن متن به خطوط
    lines = final_text.split('\n')
    current_text = ""
    
    for line_idx, line in enumerate(lines):
        # تشخیص اینکه خط آخر (قاب) هست یا نه
        is_ltr_footer = ('Licenced By' in line) or ('╭' in line) or ('╰' in line) or ('╮' in line) or ('╯' in line) or ('【' in line)
        
        if line == "":
            current_text += "\n"
            try:
                await msg.edit_text(current_text if current_text else ".", parse_mode=parse_mode)
            except Exception:
                pass
            await asyncio.sleep(0.05)
            continue

        words = line.split(' ')
        
        # برای خطوط فارسی از راست به چپ (یعنی از آخر به اول اضافه می‌کنیم که حس تایپ RTL بده)
        if not is_ltr_footer:
            words_to_iterate = words
        else:
            # برای قاب پایینی از چپ به راست
            words_to_iterate = words

        line_text = ""
        for word in words_to_iterate:
            if line_text:
                line_text += " " + word
            else:
                line_text = word

            if current_text:
                display_text = current_text + "\n" + line_text
            else:
                display_text = line_text

            try:
                await msg.edit_text(display_text, parse_mode=parse_mode)
            except BadRequest as e:
                if "not modified" not in str(e).lower():
                    pass
            except RetryAfter as e:
                await asyncio.sleep(e.retry_after)
            except Exception:
                pass
            
            await asyncio.sleep(delay)

        if current_text:
            current_text += "\n" + line_text
        else:
            current_text = line_text
            
        if line_idx < len(lines) - 1:
            current_text += "\n"
            try:
                await msg.edit_text(current_text, parse_mode=parse_mode)
            except Exception:
                pass
            await asyncio.sleep(0.05)

    try:
        await msg.edit_text(final_text, parse_mode=parse_mode, reply_markup=reply_markup)
    except BadRequest:
        try:
            await bot.send_message(
                chat_id=chat_id, 
                text=final_text, 
                parse_mode=parse_mode, 
                reply_markup=reply_markup,
                reply_to_message_id=reply_to_message_id
            )
        except Exception:
            pass
    except Exception:
        pass

    return msg
