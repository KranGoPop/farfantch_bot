from telegram import Update
from telegram.ext import ContextTypes
from .utils import pybot_db_add_user
import aiomysql
from .actions.search import search
from .actions.set_bound import set_bound
from .cbdata import decoder
from .queries.search import more
from .queries.settings import query_settings
from .queries.card import card_query


@pybot_db_add_user
async def text_router(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
  lock = context.bot_data['lock']
  conn = context.bot_data['conn']
  id = update.effective_user.id

  async with lock:
    cur = await conn.cursor(aiomysql.DictCursor)
    await cur.execute("SELECT * FROM user WHERE id = %s", (id,))
    data = await cur.fetchall()

    if len(data) == 0:
      raise ValueError("WARNING: For some unknown reason the user was not added to the db.")
    else:
      data = data[0]
    
    await cur.close()
  
  if data["mode"] == 'search':
    await search(update, context)
  else:
    await set_bound(update, context, data)


async def query_router(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
  query = update.callback_query
  await query.answer()
  callback_data = decoder(query.data)

  if callback_data["query_type"] == 'search':
    await more(update, context, callback_data)
  elif callback_data["query_type"] == 'settings':
    await query_settings(update, context, callback_data)
  elif callback_data["query_type"] == 'card':
    await card_query(update, context, callback_data)
  
