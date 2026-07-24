import logging
from telegram import Update
from telegram.ext import CommandHandler, ContextTypes
from app.config import ADMIN_USER_IDS
from app.handlers.thismonth_storage import purge_all
from app.dicts.purgeBR import PRIVATE_CHAT_ONLY, NO_PERMISSION,PURGE_SUCCESS #change this dict to purgeEN to translate the bot to english. 
logger = logging.getLogger(__name__)


async def ffpurge(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user

    if chat.type != "private":
        await update.message.reply_text(PRIVATE_CHAT_ONLY)
        return

    if not ADMIN_USER_IDS or user.id not in ADMIN_USER_IDS:
        await update.message.reply_text(NO_PERMISSION)
        return

    purge_all()
    await update.message.reply_text(PURGE_SUCCESS)


def build_purge_handler() -> CommandHandler:
    return CommandHandler("Purge", ffpurge)