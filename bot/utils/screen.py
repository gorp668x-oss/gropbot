from telegram import LinkPreviewOptions
from telegram.constants import ParseMode

from bot.utils.stream import stream_draft

DRAFT_DELAY = 0.12      # فاصله بین هر مرحله تایپ (ثانیه)
DRAFT_MAX_STEPS = 16    # حداکثر تعداد مراحل تایپ


async def show_screen(update, context, text, reply_markup=None, toast=None):
    """
    نمایش یک صفحه با حالت «ویرایشی» (تایپ تدریجی):
    ۱) نوتیف بالای صفحه  ۲) حذف پیام قبلی  ۳) تایپ تدریجی  ۴) ارسال پیام نهایی با دکمه‌ها
    """
    query = update.callback_query

    # جلوگیری از کلیک پشت‌سرهم وسط انیمیشن
    if context.user_data.get("_busy"):
        await query.answer()
        return

    context.user_data["_busy"] = True
    try:
        if toast:
            await query.answer(toast)
        else:
            await query.answer()

        chat_id = query.message.chat.id
        try:
            await query.message.delete()
        except Exception:
            pass

        await stream_draft(
            context.bot.token, chat_id, text,
            delay=DRAFT_DELAY, max_steps=DRAFT_MAX_STEPS,
        )
        await context.bot.send_message(
            chat_id,
            text,
            parse_mode=ParseMode.HTML,
            reply_markup=reply_markup,
            link_preview_options=LinkPreviewOptions(is_disabled=True),
        )
    finally:
        context.user_data["_busy"] = False