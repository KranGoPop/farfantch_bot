import aiomysql
import pymysql
import asyncio
from telegram import Update
from telegram.ext import ContextTypes
import json
import os


async def connect_to_db(loop, bot_data):
  i = 0

  with open('bot_config.json', 'r') as f:
    data = json.loads(f.read())

  while True:
    i += 1

    try:
      conn = await aiomysql.connect(
        host=os.environ.get("DB_HOST"),
        user=data["user"],
        password=data["password"],
        db=data["db"],
        loop=loop,
      )
    except pymysql.err.OperationalError:
      print(f"Trying to connect to MySQL ... ({i} try)")
      await asyncio.sleep(5)
    else:
      print("Connect to MySQL established!")
      bot_data['conn'] = conn
      return


async def add_user(update: Update, context: ContextTypes) -> None:
  id = update.message.from_user.id
  conn = context.bot_data['conn']
  lock = context.bot_data['lock']

  async with lock:
    cur = await conn.cursor(aiomysql.DictCursor)

    try:
      await cur.execute("INSERT INTO user(id, prefs) VALUES(%s, '[]')", (id,))
    except pymysql.err.DatabaseError as err:
      if err.args[0] != 1062:
        raise RuntimeError("DATABSE ERROR: " + str(err)) from err
    
    await conn.commit()
    await cur.close()
