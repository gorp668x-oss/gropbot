from telegram import LinkPreviewOptions
from telegram.constants import ParseMode


async def show_screen(update, context, text, reply_markup=None, toast=None):
    """
    نمایش یک صفحه با ویرایش همان پیام (بدون تایپ تدریجی)
    و نمایش نوتیف انیمیشنی بالای صفحه.
    """
    query = update.callback_query

    if toast:
        await query.answer(toast)
    else:
        await query.answer()

    try:
        await query.edit_message_text(
            text,
            parse_mode=ParseMode.HTML,
            reply_markup=reply_markup,
            link_preview_options=LinkPreviewOptions(is_disabled=True),
        )
    except Exception as e:
        # مثلاً «message is not modified» یا پیام خیلی قدیمی؛ مهم نیست
        print(f"show_screen edit error: {e}")