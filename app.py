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

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # Пример: https://yourname.amvera.app

app = FastAPI()

application = ApplicationBuilder().token(BOT_TOKEN).build()

def build_welcome_message(user_fullname: str):
    buttons = [
        InlineKeyboardButton("🚣 Roadmap", url="https://telegra.ph/Roadmap-05-31-2"),
        InlineKeyboardButton("📄 Whitepaper", url="https://telegra.ph/Whitepaper-06-03"),
        InlineKeyboardButton("👨‍👨‍👦 Our X", url="https://x.com/OG_IE_CTO"),
        InlineKeyboardButton("✅ Buy IE", url="https://raydium.io/swap/?inputMint=sol&outputMint=DfYVDWY1ELNpQ4s1CK5d7EJcgCGYw27DgQo2bFzMH6fA"),
    ]
    keyboard = [buttons[i:i + 2] for i in range(0, len(buttons), 2)]
    reply_markup = InlineKeyboardMarkup(keyboard)

    caption = f"👋 {user_fullname}, Welcome to the IE Community! 🌐\nYou’re early, IE is evolving from meme to ecosystem."
    video_file_id = "BAACAgIAAxkBAAMFaDo7YSsE_osC--dySL3QjJAmOZQAAj2ZAAJ0fdlJKt6TBtfs9702BA"

    return caption, video_file_id, reply_markup

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

async def user_left_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await context.bot.delete_message(
            chat_id=update.effective_chat.id,
            message_id=update.message.message_id
        )
    except Exception as e:
        logger.warning(f"Не удалось удалить сообщение о выходе: {e}")

async def send_website_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"Команда /website вызвана пользователем: {update.effective_user.id}")
    await update.message.reply_text(
        "🌐 [Link on Website](https://internet-explorercto.de/)",
        parse_mode="Markdown",
        disable_web_page_preview=True,
    )

async def send_lp_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"Команда /LP вызвана пользователем: {update.effective_user.id}")
    
    image_url = "https://i.ibb.co/20yP0WrR/raydium-pic.png"

    caption = (
        "💧 *Provide Liquidity to the IE Pool on Raydium!*\n"
        "Earn fees and farming rewards by adding liquidity.\n\n"
        "🔽 Choose an action below:"
    )
    
    buttons = [
    [
        InlineKeyboardButton("🤔 How to add Liquidity", url="https://telegra.ph/How-to-add-liquidity-06-07"),
        InlineKeyboardButton("✅ Farming IE", url="https://telegra.ph/How-to-participate-in-IE-farming-06-07")
    ],
    [
        InlineKeyboardButton("❔ FAQ", url="https://telegra.ph/FAQ-06-07-10"),
        InlineKeyboardButton("➕ Add Liquidity", url="https://raydium.io/liquidity/increase/?mode=add&pool_id=E8iZHoRdr6uJEB1VtF6JJbRz286KAh3hw8BByUQcRFTs")
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
        BotCommand("website", "Visit the official website"),
        BotCommand("LP", "Liquidity info and farming"),
    ])
application.add_handler(CommandHandler("LP", send_lp_info))
application.add_handler(CommandHandler("website", send_website_link))
application.add_handler(MessageHandler(filters.Regex(r"(?i)\b(web\s?site|site)\b"), send_website_link))
application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, new_chat_members_handler))
application.add_handler(MessageHandler(filters.StatusUpdate.LEFT_CHAT_MEMBER, user_left_handler))
application.post_init = set_bot_commands

@app.post(f"/{BOT_TOKEN}")
async def telegram_webhook(req: Request):
    data = await req.json()
    update = Update.de_json(data, application.bot)
    await application.process_update(update)
    return {"ok": True}

@app.get("/set_webhook")
async def set_webhook():
    success = await application.bot.set_webhook(url=f"{WEBHOOK_URL}/{BOT_TOKEN}")
    return {"status": "Webhook установлен" if success else "Ошибка установки"}

@app.get("/")
def root():
    return {"message": "Telegram bot is running!"}

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), reload=True)
