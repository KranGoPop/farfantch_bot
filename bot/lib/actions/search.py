from telegram import Update
from telegram.ext import ContextTypes
from functools import reduce
import re
import aiomysql
from ..utils import send_photos


async def search(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
  message = update.message.text
  print('New request: text="' + message + '"')
  message_prepare = re.sub(r'\[|\]|\\|\^|\$|\.|\?|\*|\+|\(|\)', lambda m: '\\' + m.group(), message)
  regexp = reduce(lambda s, p: s + p + '.*', message_prepare.split(' '), '.*')
  # print(regexp)

  conn = context.bot_data['conn']
  lock = context.bot_data['lock']

  user_id = update.effective_user.id

  async with lock:
    cur = await conn.cursor(aiomysql.DictCursor)
    await cur.execute("SELECT sort_order FROM user WHERE id = %s", (user_id,))
    sort_order = await cur.fetchall()

    if len(sort_order) == 0:
      raise ValueError("ERROR: For some reason the user does not exist in the DB.")
    else:
      sort_order = "DESC" if sort_order[0]["sort_order"] == 'desc' else "ASC"
    
    await cur.execute(f"SELECT s.id, s.name, s.price, s.brand, s.image, JSON_CONTAINS(u.prefs, JSON_QUOTE(s.name)) AS card FROM supplies AS s, user AS u WHERE u.id = %s AND s.price >= u.bot_bound AND s.price <= u.top_bound AND REGEXP_LIKE(search, %s) = 1 ORDER BY s.price {sort_order} LIMIT 4", (user_id, regexp,))
    items = await cur.fetchall()
    await cur.close()

  user = update.message.from_user

  await send_photos(user, items, 'part', 3, regexp)
