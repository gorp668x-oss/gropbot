import asyncio
from telegram.error import BadRequest
from telegram import InlineKeyboardMarkup

async def send_live_message(
    update,
    context,
    final_text: str,
    reply_markup: InlineKeyboardMarkup = None,
    parse_mode: str = "HTML",
    steps: int = 40,
    delay: float = 0.04
):
    """
    پیام را با افکت ویرایشی زنده (Live Editing) ارسال می‌کند.
    - ابتدا یک پیام اولیه ارسال می‌شود.
    - سپس همان پیام به صورت مرحله‌ای با edit_message_text تکمیل می‌شود.
    - در نهایت دکمه‌ها (در صورت وجود) اضافه می‌شوند.
    - در برابر خطاهای تلگرام مقاوم است و کرش نمی‌کند.
    """
    # ارسال پیام اولیه خالی (فقط یک نقطه)
    try:
        msg = await update.message.reply_text(
            ".",
            parse_mode=parse_mode
        )
    except Exception as e:
        print(f"[live_message] Failed to send initial message: {e}")
        return None

    # محاسبه گام‌ها
    total_len = len(final_text)
    if total_len == 0:
        return msg

    step_size = max(1, total_len // steps)

    current = ""
    i = step_size
    while i < total_len:
        chunk = final_text[:i]
        # فقط اگر با متن قبلی فرق داشت ویرایش کن
        if chunk != current:
            try:
                await msg.edit_text(chunk, parse_mode=parse_mode)
                current = chunk
            except BadRequest as e:
                # خطای Message is not modified نادیده گرفته شود
                if "not modified" not in str(e).lower():
                    print(f"[live_message] edit error: {e}")
            except Exception as e:
                print(f"[live_message] edit error: {e}")
        await asyncio.sleep(delay)
        i += step_size

    # پیام نهایی همراه با دکمه‌ها
    try:
        await msg.edit_text(
            final_text,
            parse_mode=parse_mode,
            reply_markup=reply_markup
        )
    except BadRequest as e:
        if "not modified" not in str(e).lower():
            print(f"[live_message] final edit error: {e}")
            # اگر ویرایش خطا داد، دکمه‌ها را در پیام جدید بفرست
            try:
                await update.message.reply_text(
                    final_text,
                    parse_mode=parse_mode,
                    reply_markup=reply_markup
                )
            except Exception:
                pass
    except Exception as e:
        print(f"[live_message] final error: {e}")

    return msg
