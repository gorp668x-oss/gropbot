import html

from telegram import Update
from telegram.ext import ContextTypes

from bot.texts.welcome import WELCOME_TEXT
from bot.texts.about import ABOUT_TEXT
from bot.texts.more_info import MORE_INFO_TEXT
from bot.texts.diff import DIFF_TEXT
from bot.keyboards.main_menu import get_main_keyboard
from bot.keyboards.back import get_back_keyboard
from bot.handlers.edit_mode import edit_mode_callback
from bot.handlers.panel import panel_callback
from bot.utils.screen import show_screen

# پیام‌های بالای صفحه (نوتیف) هنگام ورود به هر بخش
TOASTS = {
    "about": "👋 به بخش «درباره ما» خوش آمدید",
    "more_info": "📚 به بخش «اطلاعات بیشتر» خوش آمدید",
    "diff": "📊 به بخش «تفاوت نسخه‌ها» خوش آمدید",
    "back": "🏠 به منوی اصلی بازگشتید؛ خوش آمدید",
}


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data

    # callback های حالت ها
    if data.startswith("editmode_"):
        await edit_mode_callback(update, context)
        return

    if data.startswith("panel_"):
        await panel_callback(update, context)
        return

    if data == "noop":
        await query.answer()
        return

    if data == "about":
        await show_screen(update, context, ABOUT_TEXT, get_back_keyboard(), TOASTS["about"])
    elif data == "more_info":
        await show_screen(update, context, MORE_INFO_TEXT, get_back_keyboard(), TOASTS["more_info"])
    elif data == "diff":
        await show_screen(update, context, DIFF_TEXT, get_back_keyboard(), TOASTS["diff"])
    elif data == "back":
        context.user_data.pop("ticket_until", None)
        user = query.from_user
        mention = f'<a href="tg://user?id={user.id}">{html.escape(user.first_name or "کاربر")}</a>'
        await show_screen(
            update, context,
            WELCOME_TEXT.format(mention=mention),
            get_main_keyboard(),
            TOASTS["back"],
        )
    else:
        await query.answer()