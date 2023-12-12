import aiohttp
import aiomysql
import asyncio
import pymysql
import json
import os

download_counter = 0
max_pages = 0


async def connect_to_db():
  i = 0

  with open('stealer_config.json', 'r') as f:
    data = json.loads(f.read())

  while True:
    i += 1

    try:
      conn = await aiomysql.connect(
        host=os.environ.get("DB_HOST"),
        user=data["user"],
        password=data["password"],
        db=data["db"],
        loop=asyncio.get_event_loop()
      )
    except pymysql.err.OperationalError:
      print(f"STEALER: Trying to connect to MySQL ... ({i} try)")
      await asyncio.sleep(5)
    else:
      return conn 


async def fetch_data(cur, page, lock):
  global download_counter

  if page == -1:
    url = "https://server.spin4spin.com/catalog?categories=boots,shoes,sneakers,sandals&sex=m"
  else:
    url = f"https://server.spin4spin.com/catalog?categories=boots,shoes,sneakers,sandals&page={page}&sex=m"

  async with aiohttp.ClientSession() as session:
    async with session.get(url) as response:
      catalog = await response.json()

  data = [(item["brand"]["name"] + ' ' + item["name"] + ' ' + item["brand"]["name"], item["name"], int(item["price"]),
            item["brand"]["name"], item["id"] + '/' + item["images"][0]["max"]) for item in catalog['products']]

  async with lock:
    await cur.executemany("INSERT INTO supplies(`search`, `name`, `price`, `brand`, `image`) VALUES(%s, %s, %s, %s, %s)", data)

  download_counter += 1

  print(f"STEALER: Page {download_counter} of {max_pages} Downloaded;")

  return catalog['pages']


async def main():
  global max_pages
  conn = await connect_to_db()

  print('STEALER: Connect with DB has established')

  cur = await conn.cursor(aiomysql.DictCursor)

  with open('status.json', 'r') as fd:
    is_reload = json.loads(fd.read())['reload']

  if is_reload:
    await cur.execute("DELETE FROM supplies")
    with open('status.json', 'w') as fd:
      fd.write(json.dumps({"reload": False}))

    lock = asyncio.Lock()
    max_pages = await fetch_data(cur, -1, lock)

    await asyncio.gather(*[fetch_data(cur, i, lock) for i in range(2, max_pages + 1)])

  print("\nSTAELER: All pages has downloaded!")

  await cur.execute("CREATE OR REPLACE VIEW prices(max_price, min_price) AS SELECT MAX(price) AS max_price, MIN(price) AS min_price FROM supplies")

  await conn.commit()

  await cur.close()
  conn.close()


asyncio.run(main())
