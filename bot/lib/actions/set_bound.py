from telegram import Update
from telegram.ext import ContextTypes
import aiomysql


async def set_bound(update: Update, context: ContextTypes.DEFAULT_TYPE, data: dict) -> None:
  text = update.message.text
  user = update.effective_user
  conn = context.bot_data['conn']
  lock = context.bot_data['lock']
  id = user.id

  try:
    num = int(text)
  except ValueError:
    user.send_message("❌ То, что вы ввели не похоже на число.\n🤘 Попробуйте ещё...")
  
  async with lock:
    cur = await conn.cursor(aiomysql.DictCursor)
    
    await cur.execute("SELECT * FROM prices")
    prices = await cur.fetchall()

    if len(prices) == 0:
      raise TypeError("ERROR: view prices does not exist")
    else:
      prices = prices[0]
    
    if data["mode"] == 'set_bbound' and prices["max_price"] < num:
      await user.send_message("❌ Нижняя цена выходит за пределы возможного.\n🤘 Попробуйте ещё...")
    elif data["mode"] == 'set_tbound' and prices["min_price"] > num:
      await user.send_message("❌ Верхняя цена слишком низкая.\n🤘 Попробуйте ещё...")
    else:
      if data["mode"] == 'set_tbound':
        await cur.execute("UPDATE user SET top_bound = %s, mode = 'search' WHERE id = %s", (num, id,))
        await user.send_message("✔️ Верхняя цена установлена.")
      elif data["mode"] == 'set_bbound':
        await cur.execute("UPDATE user SET bot_bound = %s, mode = 'search' WHERE id = %s", (num, id,))
        await user.send_message("✔️ Нижняя цена установлена.")
    
    await conn.commit()
    await cur.close()
  
  
