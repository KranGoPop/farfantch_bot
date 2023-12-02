import logging
import os
import asyncio
import aiomysql
import pymysql
import re
from functools import reduce

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ForceReply, Update
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes, MessageHandler, filters
from telegram import constants

logging.basicConfig(
  format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


async def connect_to_db(loop, bot_data):
  i = 0

  while True:
    i += 1

    try:
      conn = await aiomysql.connect(
        host='db',
        user='db_user',
        password='1234',
        db='farfetch',
        loop=loop,
      )
    except pymysql.err.OperationalError:
      print(f"Trying to connect to MySQL ... ({i} try)")
      await asyncio.sleep(5)
    else:
      print("Connect to MySQL established!")
      bot_data['conn'] = conn
      return


async def lazy_error_handler(update, context):
  pass


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
  """Send a message when the command /start is issued."""
  user = update.effective_user
  await update.message.reply_html(
      rf"Hi {user.mention_html()}! Этот бот умеет искать кросовки на farfetch. Отправте боту любое текстовое сообщение и на его основе бот постарается найти то, что вас интересует.",
      reply_markup=ForceReply(selective=True),
  )


def get_caption(item):
  name = f"<b>{item['name']}</b>\n\n"
  price = f"Цена: {item['price']}<b>₽</b>\n"
  brand = f"Бренд: {item['brand']}"

  return name + price + brand


async def send_photos(user, data, t, n, regexp):
  if len(data) == 0:
    await user.send_message('Ничего не нашлось 😞')
    return

  if t == 'all':
    to = len(data)
  else:
    to = 2

  for i in range(to):
    if len(data) > i:
      item = data[i]
      await user.send_photo(
        'https://server.spin4spin.com/images/' + item['image'],
        get_caption(item),
        parse_mode='HTML',
      )
  
  if t == 'part':
    if len(data) == 4:
      keyboard = [[
        InlineKeyboardButton('Ещё', callback_data=regexp + ' ' + str(n) + ' ' + 'part'),
        InlineKeyboardButton('Хочу всё', callback_data=regexp + ' ' + str(n) + ' ' + 'all'),
      ]]
      reply_markup = InlineKeyboardMarkup(keyboard)
    else:
      reply_markup = None

    if len(data) > 2:
      item = data[2]
      await user.send_photo(
        'https://server.spin4spin.com/images/' + item['image'],
        get_caption(item),
        parse_mode='HTML',
        reply_markup=reply_markup,
      )

async def search(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
  message = update.message.text
  print('New request: text="' + message + '"')
  message_prepare = re.sub(r'\[|\]|\\|\^|\$|\.|\?|\*|\+|\(|\)', lambda m: '\\' + m.group(), message)
  regexp = reduce(lambda s, p: s + p + '.*', message_prepare.split(' '), '.*')
  # print(regexp)

  conn = context.bot_data['conn']
  lock = context.bot_data['lock']
  cur = await conn.cursor(aiomysql.DictCursor)

  async with lock:
    await cur.execute('SELECT * FROM supplies WHERE REGEXP_LIKE(search, %s) = 1 LIMIT 4', (regexp,))
    data = await cur.fetchall()

  # print(data)

  await cur.close()

  user = update.message.from_user

  await send_photos(user, data, 'part', 3, regexp)


async def more(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
  query = update.callback_query
  await query.answer()
  params = query.data.split(' ')
  print(params)
  user = query.from_user
  conn = context.bot_data['conn']
  lock = context.bot_data['lock']
  cur = await conn.cursor(aiomysql.DictCursor)

  if params[2] == 'all':
    async with lock:
      await cur.execute(f"SELECT * FROM supplies WHERE REGEXP_LIKE(search, %s) = 1 LIMIT {int(params[1])},18446744073709551615", (params[0],))
      data = await cur.fetchall()
  else:
    async with lock:
      await cur.execute(f"SELECT * FROM supplies WHERE REGEXP_LIKE(search, %s) = 1 LIMIT 4 OFFSET {int(params[1])}", (params[0],))
      data = await cur.fetchall()


  if params[2] == 'all':
    await send_photos(user, data, 'all', -1, '')
  else:
    await send_photos(user, data, 'part', int(params[1]) + 3, params[0])


def main() -> None:
  if os.environ.get('BOT_TOKEN') == None or os.environ.get('BOT_TOKEN') == 'your_telegram_bot_token':
    print("BOT: You should specify bot's token in config.env file")
    return

  print("Bot Started")

  application = Application.builder().token(os.environ.get('BOT_TOKEN')).build()

  application.add_handler(CommandHandler("start", start))

  application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search))
  application.add_handler(CallbackQueryHandler(more))

  # application.add_error_handler(lazy_error_handler)

  application.bot_data['lock'] = asyncio.Lock()
  
  loop = asyncio.get_event_loop()
  loop.run_until_complete(connect_to_db(loop, application.bot_data))

  application.run_polling(allowed_updates=Update.ALL_TYPES)

  application.bot_data['conn'].close()


if __name__ == "__main__":
  main()