import asyncio
import logging
import math
from html.parser import HTMLParser
from telegram.error import BadRequest, RetryAfter
from telegram import InlineKeyboardMarkup

logger = logging.getLogger(__name__)

class VisibleTextParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []
    def handle_data(self, data):
        self.parts.append(data)
    def handle_starttag(self, tag, attrs):
        if tag.lower() == "br":
            self.parts.append("\n")
    def handle_endtag(self, tag):
        if tag.lower() in ("p", "div"):
            self.parts.append("\n")
    def get_text(self):
        return "".join(self.parts)

def get_visible_text(text: str, parse_mode: str | None) -> str:
    if not parse_mode or parse_mode.upper() != "HTML":
        return text
    parser = VisibleTextParser()
    parser.feed(text)
    parser.close()
    return parser.get_text()

async def send_live_message(
    bot,
    chat_id: int,
    final_text: str,
    reply_markup: InlineKeyboardMarkup = None,
    parse_mode: str = "HTML",
    delay: float = 0.05,
    max_updates: int = 50,
):
    visible_text = get_visible_text(final_text, parse_mode)
    if not visible_text:
        return await bot.send_message(
            chat_id=chat_id,
            text=final_text,
            parse_mode=parse_mode,
            reply_markup=reply_markup,
        )

    try:
        msg = await bot.send_message(chat_id=chat_id, text="…")
    except Exception:
        logger.exception("Could not send initial live message")
        return None

    total_len = len(visible_text)
    # تعداد مراحل: سقف 50 تا
    steps = min(max_updates, max(10, total_len // 5)) 
    
    # محاسبه طول هر بلوک
    step_size = math.ceil(total_len / steps)
    
    current_pos = 0
    for i in range(0, total_len, step_size):
        current_pos = min(i + step_size, total_len)
        chunk = visible_text[:current_pos]
        
        # فقط وقتی چانک جدید با قبلی فرق داشت آپدیت کن
        if i > 0:
            try:
                await msg.edit_text(chunk)
            except BadRequest as e:
                if "not modified" not in str(e).lower():
                    pass
            except RetryAfter as e:
                # ریت لیمیت: به اندازه گفته شده صبر کن
                await asyncio.sleep(e.retry_after)
                try:
                    await msg.edit_text(chunk)
                except Exception:
                    pass
            except Exception:
                pass
            
        await asyncio.sleep(delay)

    # پیام نهایی با HTML اصلی و دکمه‌ها
    try:
        await msg.edit_text(
            final_text,
            parse_mode=parse_mode,
            reply_markup=reply_markup
        )
    except BadRequest as e:
        if "not modified" not in str(e).lower():
            try:
                await bot.send_message(
                    chat_id=chat_id,
                    text=final_text,
                    parse_mode=parse_mode,
                    reply_markup=reply_markup
                )
            except Exception:
                pass
    except Exception:
        pass

    return msg
