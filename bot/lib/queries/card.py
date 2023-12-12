from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import aiomysql
from ..cbdata import encoder
from ..utils import get_caption
import json


async def card_query(update: Update, context: ContextTypes.DEFAULT_TYPE, callback_data: dict) -> None:
  conn = context.bot_data["conn"]
  lock = context.bot_data["lock"]
  query = update.callback_query
  user_id = query.from_user.id

  async with lock:
    cur = await conn.cursor(aiomysql.DictCursor)
    await cur.execute("SELECT name, price, brand, image FROM supplies WHERE id = %s", (callback_data["id"],))
    item = await cur.fetchall()

    if len(item) == 0:
      raise TypeError(f"ERROR: For some reason the product with id - {callback_data['id']} not found")
    else:
      item = item[0]

    await cur.execute("SELECT prefs FROM user WHERE id = %s", (user_id,))
    prefs = await cur.fetchall()

    if len(prefs) == 0:
      raise TypeError(f"ERROR: For some reason the user not found")
    else:
      prefs = json.loads(prefs[0]["prefs"])

    if item["name"] not in prefs:
      prefs.append(item["name"])
      await cur.execute("UPDATE user SET prefs = %s WHERE id = %s", (json.dumps(prefs), user_id,))
      await conn.commit()
  
  item["card"] = True

  if callback_data.get("offset") != None:
    markup = InlineKeyboardMarkup([[
        InlineKeyboardButton(
          'Ещё',
          callback_data=encoder(
            {
              "query_type": "search",
              "regexp": callback_data["regexp"],
              "offset": callback_data["offset"],
              "type": "part",
            }
          )
        ),
        InlineKeyboardButton(
          'Хочу всё',
          callback_data=encoder({
            "query_type": "search",
            "regexp": callback_data["regexp"],
            "offset": callback_data["offset"],
            "type": "all",
          })
        ),
      ]])
  else:
    markup = None

  await query.edit_message_caption(
    get_caption(item),
    reply_markup=markup,
    parse_mode='HTML'
  )
