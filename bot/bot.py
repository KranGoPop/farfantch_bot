import logging
import os
import asyncio
from lib import db
from lib.commands.start import start
from lib.commands.settings import settings
from lib.router import text_router, query_router

from telegram import Update
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes, MessageHandler, filters

logging.basicConfig(
  format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


async def lazy_error_handler(update, context):
  pass


def main() -> None:
  if os.environ.get('BOT_TOKEN') == None or os.environ.get('BOT_TOKEN') == 'your_telegram_bot_token':
    print("BOT: You should specify bot's token in config.env file")
    return

  print("Bot Started")

  application = Application.builder().token(os.environ.get('BOT_TOKEN')).build()

  application.add_handler(CommandHandler("start", start))
  application.add_handler(CommandHandler("settings", settings))

  application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_router))
  application.add_handler(CallbackQueryHandler(query_router))

  # application.add_error_handler(lazy_error_handler)

  application.bot_data['lock'] = asyncio.Lock()
  
  loop = asyncio.get_event_loop()
  loop.run_until_complete(db.connect_to_db(loop, application.bot_data))

  application.run_polling(allowed_updates=Update.ALL_TYPES)

  # application.bot_data['conn'].close()


if __name__ == "__main__":
  main()