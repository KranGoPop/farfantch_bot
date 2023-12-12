from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import aiomysql
from ..utils import get_main_settings_page, send_photos
from ..cbdata import encoder


async def get_bound_set_page(conn, lock, subst: str) -> tuple[str, InlineKeyboardMarkup]:
  async with lock:
    cur = await conn.cursor(aiomysql.DictCursor)
    await cur.execute("SELECT * FROM prices")
    prices = await cur.fetchall()

  if len(prices) == 0:
    raise TypeError("ERROR: view prices does not exist")
  else:
    prices = prices[0]
  
  answer = f"⚙️ Настройки {subst} границы поиска ⚙️\n\n"
  answer += f"Текущий ценовой разброс товаров в наличии:\n"
  answer += f"  от <b>{prices['min_price']}₽</b> до <b>{prices['max_price']}₽</b>.\n"
  answer += "Укажите цену в сообщении."

  markup = InlineKeyboardMarkup([[
    InlineKeyboardButton("👈 Назад", callback_data=encoder({
      "query_type": "settings",
      "type": "to_main",
    }))
  ]])

  return (answer, markup)


async def get_prefs_page():
  return ("Вот ваша корзина 👇", None)

async def get_set_order_page():
  return (
    "⚖️ Выберете сортировку элементов в выдаче поиска.",
    InlineKeyboardMarkup([
      [
        InlineKeyboardButton('Возростание', callback_data=encoder({
          "query_type": "settings",
          "type": "set_asc",
        })),
        InlineKeyboardButton('Убывание', callback_data=encoder({
          "query_type": "settings",
          "type": "set_desc",
        }))
      ],
      [InlineKeyboardButton("👈 Назад", callback_data=encoder({
        "query_type": "settings",
        "type": "to_main",
      }))]
    ])
  )


async def query_settings(update: Update, context: ContextTypes.DEFAULT_TYPE, callback_data: dict) -> None:
  stype = callback_data["type"]
  lock = context.bot_data["lock"]
  conn = context.bot_data["conn"]
  query = update.callback_query
  user = query.from_user
  user_id = user.id

  async with lock:
    cur = await conn.cursor(aiomysql.DictCursor)

    if stype == "set_tbound":
      await cur.execute("UPDATE user SET mode = 'set_tbound' WHERE id = %s", (user_id,))
      getter_func = get_bound_set_page(conn, lock, "Верхней")

    elif stype == "remove_tbound":
      await cur.execute("UPDATE user SET top_bound = 16777215 WHERE id = %s", (user_id,))
      await user.send_message("ℹ️ Верхняя граница цены поиска убрана.")
      getter_func = get_main_settings_page(conn, lock, user_id)

    elif stype == "set_bbound":
      await cur.execute("UPDATE user SET mode = 'set_bbound' WHERE id = %s", (user_id,))
      getter_func = get_bound_set_page(conn, lock, "Нижней")
      
    elif stype == "remove_bbound":
      await cur.execute("UPDATE user SET bot_bound = 0 WHERE id = %s", (user_id,))
      await user.send_message("ℹ️ Нижняя граница цены поиска убрана.")
      getter_func = get_main_settings_page(conn, lock, user_id)

    elif stype == "show_prefs":
      await cur.execute("SELECT s.id, s.name, s.price, s.brand, s.image, 1 AS card FROM supplies AS s, user AS u WHERE u.id = %s AND JSON_CONTAINS(u.prefs, JSON_QUOTE(s.name)) = 1", (user_id,))
      items = await cur.fetchall()
      await send_photos(user, items, "all", -1, '')
      getter_func = get_prefs_page()

    elif stype == "remove_prefs":
      await cur.execute("UPDATE user SET prefs = '[]' WHERE id = %s", (user_id,))
      await user.send_message("ℹ️ Корзина очищена.")
      getter_func = get_main_settings_page(conn, lock, user_id)
    
    elif stype == "to_main":
      getter_func = get_main_settings_page(conn, lock, user_id)
    
    elif stype == "set_order":
      getter_func = get_set_order_page()
    
    elif stype == "set_desc":
      await cur.execute("UPDATE user SET sort_order = 'desc' WHERE id = %s", (user_id,))
      getter_func = get_main_settings_page(conn, lock, user_id)

    elif stype == "set_asc":
      await cur.execute("UPDATE user SET sort_order = 'asc' WHERE id = %s", (user_id,))
      getter_func = get_main_settings_page(conn, lock, user_id)
    
    await conn.commit()
    await cur.close()
  
  page, markup = await getter_func

  await query.edit_message_text(page, parse_mode='HTML', reply_markup=markup)