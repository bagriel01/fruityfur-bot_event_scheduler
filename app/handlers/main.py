import logging
import asyncio
from datetime import datetime as dt
import pytz
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    ChatMemberHandler,
)
import app
from app.config import BOT_TOKEN, WEBHOOK_URL, PORT
from app.handlers.scheduler import build_ffpost_handler, build_approval_handler
from app.handlers.thismonth import build_ffthismonth_handler
from app.handlers.purge import build_purge_handler
from app.handlers.ffremove import build_ffremove_handler
from app.dicts.mainBR import START, PING, HELP, PRIVACY, HANDLER_ADD_TO_GROUP   #change this dict to mainEN to translate the bot to english. 
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        START
    )


async def FFPing(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tz = pytz.timezone("America/Sao_Paulo")
    now = dt.now(tz)

    await update.message.reply_text(
        PING.format(now.strftime("%d/%m/%Y %H:%M"))
    )


async def FFHelp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        HELP
    )

async def FFPrivacy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        PRIVACY
    )


async def handle_bot_added_to_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    result = update.my_chat_member
    if not result:
        return
    old_status = result.old_chat_member.status
    new_status = result.new_chat_member.status
    if old_status in ("left", "kicked") and new_status in ("member", "administrator"):
        await context.bot.send_message(
            chat_id=result.chat.id,
            text=HANDLER_ADD_TO_GROUP,
        )


def main():
    if not BOT_TOKEN:
        raise RuntimeError("Epic Sadface: BOT_TOKEN not defined")

    if not WEBHOOK_URL:
        raise RuntimeError("Epic Sadface: WEBHOOK_URL not defined")

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("FFPing", FFPing))
    app.add_handler(CommandHandler("FFHelp", FFHelp))
    app.add_handler(CommandHandler("FFPrivacy", FFPrivacy))
    app.add_handler(build_approval_handler())
    app.add_handler(build_ffpost_handler())
    app.add_handler(build_ffthismonth_handler())
    app.add_handler(build_purge_handler())
    for handler in build_ffremove_handler():
        app.add_handler(handler)
    app.add_handler(
        ChatMemberHandler(handle_bot_added_to_group, ChatMemberHandler.MY_CHAT_MEMBER)
    )
    webhook_path = f"/webhook/{BOT_TOKEN}"
    webhook_url = f"{WEBHOOK_URL}{webhook_path}"

    logger.info(f"Iniciando Webhook em {webhook_url}")

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=webhook_path,
        webhook_url=webhook_url,
    )


if __name__ == "__main__":
    main()
