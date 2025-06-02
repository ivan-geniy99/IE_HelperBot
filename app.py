import os
import logging
from flask import Flask, request
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, filters, CallbackContext, ChatMemberHandler

TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # Укажи как https://yourname.amvera.app/<TOKEN>

bot = Bot(token=TOKEN)

app = Flask(__name__)

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

dispatcher = Dispatcher(bot=bot, update_queue=None, use_context=True)

# Приветственное сообщение с кнопками
def build_welcome_message(user_fullname: str):
    buttons = [
        InlineKeyboardButton("🛣 Roadmap", url="https://telegra.ph/Roadmap-05-31-2"),
        InlineKeyboardButton("📄 Whitepaper", url="https://telegra.ph/Whitepaper-05-31"),
        InlineKeyboardButton("👨‍👩‍👦‍👦 Our X", url="https://x.com/OG_IE_CTO"),
        InlineKeyboardButton("✅ Buy IE", url="https://raydium.io/swap/?inputMint=sol&outputMint=DfYVDWY1ELNpQ4s1CK5d7EJcgCGYw27DgQo2bFzMH6fA")
    ]
    keyboard = [buttons[i:i+2] for i in range(0, len(buttons), 2)]
    reply_markup = InlineKeyboardMarkup(keyboard)

    caption = f"👋 {user_fullname}, Welcome to the IE Community! 🌐\nYou’re early, IE is evolving from meme to ecosystem."
    video_file_id = "BAACAgIAAxkBAAMFaDo7YSsE_osC--dySL3QjJAmOZQAAj2ZAAJ0fdlJKt6TBtfs9702BA"

    return caption, video_file_id, reply_markup

# Обработчики
def new_chat_members_handler(update: Update, context: CallbackContext):
    for member in update.message.new_chat_members:
        username = member.username or ""
        if "bot" in username.lower():
            logger.info(f"Пропущен бот: @{username}")
            continue

        user_name = member.full_name
        caption, video_file_id, reply_markup = build_welcome_message(user_name)

        context.bot.send_video(
            chat_id=update.effective_chat.id,
            video=video_file_id,
            caption=caption,
            reply_markup=reply_markup,
        )

def send_website_link(update: Update, context: CallbackContext):
    logger.info(f"Команда /website вызвана пользователем: {update.effective_user.id}")
    update.message.reply_text(
        "🌐 [Link on Website](https://internet-explorercto.de/)",
        parse_mode="Markdown", disable_web_page_preview=True
    )

# Настройка команд
def set_bot_commands(context: CallbackContext):
    context.bot.set_my_commands([
        BotCommand("website", "Visit the official website"),
    ])

# Webhook endpoint
@app.route(f'/{TOKEN}', methods=['POST'])
def webhook_handler():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return 'ok'

# Endpoint установки webhook (один раз через браузер)
@app.route('/set_webhook', methods=['GET'])
def set_webhook():
    success = bot.set_webhook(url=f"{WEBHOOK_URL}/{TOKEN}")
    return f"Webhook {'set successfully' if success else 'failed to set'}."

# Простой индекс для проверки доступности
@app.route('/', methods=['GET'])
def index():
    return "Telegram bot is running!"

# Регистрация хендлеров
dispatcher.add_handler(CommandHandler("website", send_website_link))
dispatcher.add_handler(MessageHandler(filters.Regex(r"(?i)\b(web\s?site|site)\b"), send_website_link))
dispatcher.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, new_chat_members_handler))

# Установка команд при старте
set_bot_commands(CallbackContext(dispatcher))

# Запуск сервера
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
