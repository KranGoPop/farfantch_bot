from telegram import Update, User, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from .db import add_user
import json
import aiomysql
from functools import reduce
from .cbdata import encoder

def pybot_db_add_user(func):
  async def wrapp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await add_user(update, context)
    await func(update, context)
  
  return wrapp


def get_caption(item: dict) -> str:
  name = f"<b>{item['name']}</b>\n\n"
  price = f"Цена: {item['price']}<b>₽</b>\n"
  brand = f"Бренд: {item['brand']}"

  if item["card"]:
    card = f"\n\n❤️ Товар в корзине."
  else:
    card = ''

  return name + price + brand + card


async def send_photos(user: User, items: dict, send_type: str, offset: int, regexp: str) -> None:
  if len(items) == 0:
    await user.send_message('Ничего не нашлось 😞')
    return

  if send_type == 'all':
    to = len(items)
  else:
    to = 2

  for i in range(to):
    if len(items) > i:
      item = items[i]

      keyboard = []

      if not item["card"]:
        keyboard.append([InlineKeyboardButton(
          '🛍️👈 В корзину',
          callback_data=encoder({
            "query_type": "card",
            "id": items[i]["id"],
          })
        )])
      
      await user.send_photo(
        'https://server.spin4spin.com/images/' + item['image'],
        get_caption(item),
        parse_mode='HTML',
        reply_markup=InlineKeyboardMarkup(keyboard),
      )
  
  if send_type == 'part':
    if len(items) == 4:
      keyboard = []

      if not items[2]["card"]:
        keyboard.append([InlineKeyboardButton(
          '🛍️👈 В корзину',
          callback_data=encoder({
            "query_type": "card",
            "id": items[2]["id"],
            "offset": offset,
            "regexp": regexp,
          })
        )])
      keyboard.append([
        InlineKeyboardButton(
          'Ещё',
          callback_data=encoder(
            {
              "query_type": "search",
              "regexp": regexp,
              "offset": offset,
              "type": "part",
            }
          )
        ),
        InlineKeyboardButton(
          'Хочу всё',
          callback_data=encoder({
            "query_type": "search",
            "regexp": regexp,
            "offset": offset,
            "type": "all",
          })
        ),
      ])

      reply_markup = InlineKeyboardMarkup(keyboard)
    else:
      reply_markup = None

    if len(items) > 2:
      item = items[2]
      await user.send_photo(
        'https://server.spin4spin.com/images/' + item['image'],
        get_caption(item),
        parse_mode='HTML',
        reply_markup=reply_markup,
      )


def get_query_settings_cbdata(callback_data: str) -> str:
  return encoder({
    "query_type": "settings",
    "type": callback_data
  })

async def get_main_settings_page(conn, lock, user_id) -> tuple[str, InlineKeyboardMarkup]:
  async with lock:
    cur = await conn.cursor(aiomysql.DictCursor)

    await cur.execute("SELECT * FROM prices")
    prices = await cur.fetchall()

    if len(prices) == 0:
      raise TypeError("ERROR: view prices does not exist")
    else:
      prices = prices[0]

    await cur.execute("SELECT * FROM user WHERE id = %s", (user_id,))
    user_data = await cur.fetchall()

    if len(user_data) == 0:
      raise ValueError("ERROR: For some reason the user does not exist in the DB.")
    else:
      user_data = user_data[0]
    
    await cur.close()

  answer = "⚙️ Настройки ⚙️\n\n"

  answer += f"Тоавры в поиске сортируются <b>По {'убыванию' if user_data['sort_order'] == 'desc' else 'возростанию'}</b> цены.\n\n"

  if user_data["top_bound"] == 16777215 and user_data["bot_bound"] == 0:
    answer += "У вас не установлен фильктр цен.\n\n"
  elif user_data["bot_bound"] == 0:
    answer += f"У вас установлен фильктр цен.\nБудут показаны товары до <b>{user_data['top_bound']}₽</b>.\n\n"
  elif user_data["top_bound"] == 16777215:
    answer += f"У вас установлен фильктр цен.\nБудут показаны товары от <b>{user_data['bot_bound']}₽</b>.\n\n"
  else:
    answer += f"У вас установлен фильктр цен.\nБудут показаны товары от <b>{user_data['bot_bound']}₽</b> и до <b>{user_data['top_bound']}₽</b>.\n\n"
  
  prefs_count = reduce(lambda c, _: c + 1, json.loads(user_data['prefs']), 0)
  answer += f"У вас в корзине товаров: <b>{prefs_count}</b>."

  markup = []

  markup.append([InlineKeyboardButton('⚙️ Сортировку', callback_data=get_query_settings_cbdata("set_order"))])
  markup.append([InlineKeyboardButton('⚙️ Макс. Цену', callback_data=get_query_settings_cbdata("set_tbound"))])

  if user_data["top_bound"] != 16777215:
    markup.append([InlineKeyboardButton('❌ Макс. Цену', callback_data=get_query_settings_cbdata("remove_tbound"))])
  
  markup.append([InlineKeyboardButton('⚙️ Мин. Цену', callback_data=get_query_settings_cbdata("set_bbound"))])

  if user_data["bot_bound"] != 0:
    markup.append([InlineKeyboardButton('❌ Мин. Цену', callback_data=get_query_settings_cbdata("remove_bbound"))])
  
  if prefs_count != 0:
    markup.append([InlineKeyboardButton('🛍️ Показать корзину', callback_data=get_query_settings_cbdata("show_prefs"))])
    markup.append([InlineKeyboardButton('❌ Отчистить корзину', callback_data=get_query_settings_cbdata("remove_prefs"))])

  return answer, InlineKeyboardMarkup(markup)