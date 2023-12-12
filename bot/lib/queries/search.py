from telegram import Update
from telegram.ext import ContextTypes
import aiomysql
from ..utils import send_photos


async def more(update: Update, context: ContextTypes.DEFAULT_TYPE, callback_data: dict) -> None:
  query = update.callback_query
  user = query.from_user
  conn = context.bot_data['conn']
  lock = context.bot_data['lock']
  user_id = user.id

  async with lock:
    cur = await conn.cursor(aiomysql.DictCursor)

    await cur.execute("SELECT sort_order FROM user WHERE id = %s", (user_id,))
    sort_order = await cur.fetchall()

    if len(sort_order) == 0:
      raise ValueError("ERROR: For some reason the user does not exist in the DB.")
    else:
      sort_order = "DESC" if sort_order[0]["sort_order"] == 'desc' else "ASC"

    if callback_data["type"] == 'all':
      await cur.execute(f"SELECT s.id, s.name, s.price, s.brand, s.image, JSON_CONTAINS(u.prefs, JSON_QUOTE(s.name)) AS card FROM supplies AS s, user AS u WHERE u.id = %s AND s.price >= u.bot_bound AND s.price <= u.top_bound AND REGEXP_LIKE(search, %s) = 1 ORDER BY s.price {sort_order} LIMIT {int(callback_data['offset'])},18446744073709551615", (user_id, callback_data["regexp"],))
      items = await cur.fetchall()
    else:
      await cur.execute(f"SELECT s.id, s.name, s.price, s.brand, s.image, JSON_CONTAINS(u.prefs, JSON_QUOTE(s.name)) AS card FROM supplies AS s, user AS u WHERE u.id = %s AND s.price >= u.bot_bound AND s.price <= u.top_bound AND REGEXP_LIKE(search, %s) = 1 ORDER BY s.price {sort_order} LIMIT 4 OFFSET {int(callback_data['offset'])}", (user_id, callback_data["regexp"],))
      items = await cur.fetchall()
    
    await cur.close()


  if callback_data["type"] == 'all':
    await send_photos(user, items, 'all', -1, '')
  else:
    await send_photos(user, items, 'part', callback_data["offset"] + 3, callback_data["regexp"])