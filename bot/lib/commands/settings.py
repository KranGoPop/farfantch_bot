from ..utils import pybot_db_add_user
from telegram import Update
from telegram.ext import ContextTypes
from ..utils import get_main_settings_page


@pybot_db_add_user
async def settings(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
  conn = context.bot_data["conn"]
  lock = context.bot_data["lock"]
  user = update.effective_user
  id = user.id

  main_page, markup = await get_main_settings_page(conn, lock, id)

  await user.send_message(
    text=main_page,
    parse_mode='HTML',
    reply_markup=markup
  )