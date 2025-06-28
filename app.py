import os
import logging
from fastapi import FastAPI, Request
from telegram import BotCommand, InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
import uvicorn
from stop_words import is_spam_message, contains_blocked_id
from contextlib import asynccontextmanager
from urllib.parse import unquote
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

# Логгирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Переменные окружения
BOT_TOKEN = os.environ.get("BOT_TOKEN")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")  
TARGET_CHAT_ID = os.environ.get("TARGET_CHAT_ID")

# Инициализация FastAPI и Telegram Bot
application = ApplicationBuilder().token(BOT_TOKEN).build()

# Lifespan manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    await application.initialize()
    await application.start()
    await set_bot_commands()

    # Настройка планировщика
    scheduler = AsyncIOScheduler()

    scheduler.add_job(send_vote_reminder, IntervalTrigger(hours=4))
    scheduler.add_job(send_good_morning, CronTrigger(hour=9, minute=0))

    scheduler.start()

    yield

    await application.stop()
    await application.shutdown()

# FastAPI app с lifespan
app = FastAPI(lifespan=lifespan)

def build_welcome_message(user_fullname: str):
    buttons = [
        InlineKeyboardButton("🛣 Roadmap", url="https://telegra.ph/Roadmap-05-31-2"),
        InlineKeyboardButton("📄 Whitepaper", url="https://telegra.ph/Whitepaper-06-03"),
        InlineKeyboardButton("👨‍👨‍👦 Our X", url="https://x.com/OG_IE_CTO"),
        InlineKeyboardButton("✅ Buy IE", url="https://raydium.io/swap/?inputMint=sol&outputMint=DfYVDWY1ELNpQ4s1CK5d7EJcgCGYw27DgQo2bFzMH6fA"),
    ]
    keyboard = [buttons[i:i + 2] for i in range(0, len(buttons), 2)]
    reply_markup = InlineKeyboardMarkup(keyboard)

    caption = (
        f"👋 {user_fullname}, Welcome to the IE Community! 🌐\n"
        "You’re early, IE is evolving from meme to ecosystem."
    )
    video_file_id = "BAACAgIAAxkBAAMFaDo7YSsE_osC--dySL3QjJAmOZQAAj2ZAAJ0fdlJKt6TBtfs9702BA"

    return caption, video_file_id, reply_markup

async def send_vote_reminder():
    try:
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🗳 Vote on WTF", url="https://t.me/WTFTrendingBot?start=vote_DfYVDWY1ELNpQ4s1CK5d7EJcgCGYw27DgQo2bFzMH6fA"),
                InlineKeyboardButton("🗳 Vote on Major BB", url="https://t.me/MajorBuyBot?start=vote_-1002366046946")
            ]
        ])

        await application.bot.send_message(
            chat_id=TARGET_CHAT_ID,
            text="Keep voting, explorers! 😎",
            reply_markup=keyboard
        )
        logger.info("Отправлено сообщение-напоминание о голосовании с кнопками.")
    except Exception as e:
        logger.error(f"Ошибка при отправке напоминания о голосовании: {e}")

async def send_good_morning():
    try:
        await application.bot.send_message(
            chat_id=TARGET_CHAT_ID,
            text="Gm, explorers! 😛"
        )
        logger.info("Отправлено утреннее сообщение.")
    except Exception as e:
        logger.error(f"Ошибка при отправке утреннего сообщения: {e}")

async def new_chat_members_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
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

async def delete_message_if_match(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    content = update.message.text or update.message.caption
    if not content:
        return

    # Исключаем разрешённые команды
    allowed_commands = ["/website"]
    command = content.strip().split()[0].lower()
    if command in allowed_commands and not contains_blocked_id(content):
        return

    if is_spam_message(content):
        try:
            await context.bot.delete_message(
                chat_id=update.effective_chat.id,
                message_id=update.message.message_id
            )
            logger.info(f"Удалено сообщение от пользователя {update.effective_user.id}: {repr(content)}")
        except Exception as e:
            logger.warning(f"Ошибка при удалении сообщения: {e}")
        return

async def user_left_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await context.bot.delete_message(
            chat_id=update.effective_chat.id,
            message_id=update.message.message_id
        )
    except Exception as e:
        logger.warning(f"Не удалось удалить сообщение о выходе: {e}")


async def send_website_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🌐 [Link on Website](https://internet-explorercto.de/)",
        parse_mode="Markdown",
        disable_web_page_preview=True,
    )

async def send_content_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤙 [Link on Content Group](https://t.me/Content_IE)",
        parse_mode="Markdown",
        disable_web_page_preview=True,
    )


async def send_lp_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"Команда /LP вызвана пользователем: {update.effective_user.id}")

    image_url = "https://i.ibb.co/20yP0WrR/raydium-pic.png"
    caption = (
        "💧 *Provide Liquidity to the IE Pool on Raydium!*\n\n"
        "Earn fees and farming rewards by adding liquidity.\n\n"
        "🔽 Choose an action below:"
    )
    buttons = [
        [
            InlineKeyboardButton("🤔 How to add Liquidity", url="https://telegra.ph/How-to-add-liquidity-06-07"),
            InlineKeyboardButton("👨‍🌾 Farming IE", url="https://telegra.ph/How-to-participate-in-IE-farming-06-07")
        ],
        [
            InlineKeyboardButton("❔ FAQ", url="https://telegra.ph/FAQ-06-07-10"),
            InlineKeyboardButton("💰 Add Liquidity", url="https://raydium.io/liquidity/increase/?mode=add&pool_id=E8iZHoRdr6uJEB1VtF6JJbRz286KAh3hw8BByUQcRFTs")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(buttons)

    await update.message.reply_photo(
        photo=image_url,
        caption=caption,
        parse_mode="Markdown",
        reply_markup=reply_markup
    )


async def set_bot_commands():
    await application.bot.set_my_commands([
        BotCommand("website", "Official website"),
        BotCommand("content", "Check it out and share!"),
    ])


# Регистрация хендлеров
#application.add_handler(CommandHandler("lp", send_lp_info), group=1) пока что убрал, потому что нет фармингов
#Первая группа
application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, new_chat_members_handler), group=0)
application.add_handler(MessageHandler(filters.StatusUpdate.LEFT_CHAT_MEMBER, user_left_handler), group=0)
#Вторая группа
application.add_handler(CommandHandler("website", send_website_link), group=1)
application.add_handler(MessageHandler(filters.Regex(r"(?i)\b(web\s?site|site)\b"), send_website_link), group=1)
application.add_handler(CommandHandler("content", send_content_group), group=1)
application.add_handler(MessageHandler(filters.Regex(r"(?i)\bcontents?\b"), send_website_link), group=1)
#Третья группа
application.add_handler(MessageHandler(filters.ALL, delete_message_if_match), group=2)


application.post_init = set_bot_commands


# Webhook endpoint
@app.post(f"/{unquote(BOT_TOKEN)}")
async def telegram_webhook(req: Request):
    data = await req.json()
    update = Update.de_json(data, application.bot)
    await application.process_update(update)
    return {"ok": True}


# Установка webhook
@app.get("/set_webhook")
async def set_webhook():
    success = await application.bot.set_webhook(url=f"{WEBHOOK_URL}/{BOT_TOKEN}")
    return {"status": "Webhook установлен" if success else "Ошибка установки"}


# Простой корневой маршрут
@app.get("/")
def root():
    return {"message": "Telegram bot is running!"}


# Запуск приложения
if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=int(os.environ.get("PORT", 80)))
