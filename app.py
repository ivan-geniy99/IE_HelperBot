import os
import logging
from flask import Flask, request
from telegram import BotCommand, InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Получение токена и URL вебхука из переменных окружения
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # Пример: https://yourname.amvera.app

# Инициализация Flask-приложения
app = Flask(__name__)

# Создание экземпляра приложения Telegram
application = ApplicationBuilder().token(BOT_TOKEN).build()

# Функция для построения приветственного сообщения
def build_welcome_message(user_fullname: str):
    buttons = [
        InlineKeyboardButton("🛣 Roadmap", url="https://telegra.ph/Roadmap-05-31-2"),
        InlineKeyboardButton("📄 Whitepaper", url="https://telegra.ph/Whitepaper-05-31"),
        InlineKeyboardButton("👨‍👩‍👦‍👦 Our X", url="https://x.com/OG_IE_CTO"),
        InlineKeyboardButton("✅ Buy IE", url="https://raydium.io/swap/?inputMint=sol&outputMint=DfYVDWY1ELNpQ4s1CK5d7EJcgCGYw27DgQo2bFzMH6fA"),
    ]
    keyboard = [buttons[i:i+2] for i in range(0, len(buttons), 2)]
    reply_markup = InlineKeyboardMarkup(keyboard)

    caption = f"👋 {user_fullname}, Welcome to the IE Community! 🌐\nYou’re early, IE is evolving from meme to ecosystem."
    video_file_id = "BAACAgIAAxkBAAMFaDo7YSsE_osC--dySL3QjJAmOZQAAj2ZAAJ0fdlJKt6TBtfs9702BA"

    return caption, video_file_id, reply_markup

# Обработчик новых участников чата
# Обработчик новых участников чата
async def new_chat_members_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        # Удаляем системное сообщение о вступлении пользователя
        await context.bot.delete_message(
            chat_id=update.effective_chat.id,
            message_id=update.message.message_id
        )
    except Exception as e:
        logger.warning(f"Не удалось удалить системное сообщение: {e}")

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

# Удаление уведомлений о выходе из чата
async def user_left_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await context.bot.delete_message(
            chat_id=update.effective_chat.id,
            message_id=update.message.message_id
        )
    except Exception as e:
        logger.warning(f"Не удалось удалить сообщение о выходе: {e}")


# Обработчик команды /website
async def send_website_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"Команда /website вызвана пользователем: {update.effective_user.id}")
    await update.message.reply_text(
        "🌐 [Link on Website](https://internet-explorercto.de/)",
        parse_mode="Markdown",
        disable_web_page_preview=True,
    )

# Установка команд бота
async def set_bot_commands():
    await application.bot.set_my_commands([
        BotCommand("website", "Visit the official website"),
    ])

# Регистрация обработчиков
application.add_handler(CommandHandler("website", send_website_link))
application.add_handler(MessageHandler(filters.Regex(r"(?i)\b(web\s?site|site)\b"), send_website_link))
application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, new_chat_members_handler))
application.add_handler(MessageHandler(filters.StatusUpdate.LEFT_CHAT_MEMBER, user_left_handler))

# Установка команд при запуске
application.post_init = set_bot_commands

# Обработка входящих обновлений через вебхук
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
async def webhook_handler():
    update = Update.de_json(request.get_json(force=True), application.bot)
    await application.process_update(update)
    return "ok"

# Установка вебхука
@app.route("/set_webhook", methods=["GET"])
async def set_webhook():
    success = await application.bot.set_webhook(url=f"{WEBHOOK_URL}/{BOT_TOKEN}")
    return f"Webhook {'успешно установлен' if success else 'не удалось установить'}."

# Проверка доступности сервера
@app.route("/", methods=["GET"])
def index():
    return "Telegram bot is running!"

# Запуск Flask-приложения
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

