from telegram import Update
from telegram.ext import ContextTypes
from ..utils import pybot_db_add_user


@pybot_db_add_user
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
  """Send a message when the command /start is issued."""
  user = update.effective_user
  await user.send_message(
    text=rf"Hi {user.mention_html()}! Этот бот умеет искать кросовки на farfetch. Отправте боту любое текстовое сообщение и на его основе бот постарается найти то, что вас интересует.",
  )
