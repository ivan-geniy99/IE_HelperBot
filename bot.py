import re
from telegram import BotCommand
import logging
import os

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters, ChatMemberHandler, CommandHandler


BOT_TOKEN = os.environ["BOT_TOKEN"]

# Включаем логгирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Приветственное сообщение с кнопками
def build_welcome_message(user_fullname: str):
    buttons = [
        InlineKeyboardButton("🛣 Roadmap", url="https://telegra.ph/Roadmap-05-31-2"),
        InlineKeyboardButton("📄 Whitepaper", url="https://telegra.ph/Whitepaper-05-31"),
        InlineKeyboardButton("👨‍👩‍👦‍👦 Our X", url="https://x.com/OG_IE_CTO"),
        InlineKeyboardButton("✅ Buy IE", url="https://raydium.io/swap/?inputMint=sol&outputMint=DfYVDWY1ELNpQ4s1CK5d7EJcgCGYw27DgQo2bFzMH6fA")
    ]

    # Группировка кнопок по 2 в ряду
    keyboard = [buttons[i:i+2] for i in range(0, len(buttons), 2)]
    reply_markup = InlineKeyboardMarkup(keyboard)

    caption = f"👋 {user_fullname}, Welcome to the IE Community! 🌐\nYou’re early, IE is evolving from meme to ecosystem."
    video_file_id = "BAACAgIAAxkBAAMFaDo7YSsE_osC--dySL3QjJAmOZQAAj2ZAAJ0fdlJKt6TBtfs9702BA"  # Заменить на свой URL

    return caption, video_file_id, reply_markup

# Обработчик новых участников
async def new_chat_members_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for member in update.message.new_chat_members:
        username = member.username or ""
        if "bot" in username.lower():
            logger.info(f"Пропущен бот: @{username}")
            continue

        user_name = member.full_name
        caption, video_file_id, reply_markup = build_welcome_message(user_name)

        await context.bot.send_video(
            chat_id=update.effective_chat.id,
            video=video_file_id,
            caption=caption,
            reply_markup=reply_markup,
        )
#Команда отправки ссылки на сайт        
async def send_website_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"send_website_link вызван с текстом: {update.message.text}")
    await update.message.reply_text(
        "🌐 [Link on Website](https://internet-explorercto.de/)",
        parse_mode="Markdown", disable_web_page_preview=True
    )
#Команды 
async def on_startup(app):
    await app.bot.set_my_commands([
        BotCommand("website", "Visit the official website"),
    ])

# Основной запуск бота
if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.post_init = on_startup
    app.add_handler(CommandHandler("website", send_website_link))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, new_chat_members_handler))
    app.add_handler(MessageHandler(
    filters.TEXT & filters.Regex(r"(?i)\b(web\s?site|site)\b"),
    send_website_link
))


    app.run_polling()
