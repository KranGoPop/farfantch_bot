def convert_integer(decimal):
  number = ''
  while decimal > 0:
    decimal, remainder = divmod(decimal, 36)
    if remainder > 9:
      remainder = chr(ord('A') + remainder - 10)
    number = str(remainder) + number
  return number


def encoder(data: dict) -> str:
  setting_types = {
    "set_tbound": 0,
    "remove_tbound": 1,
    "set_bbound": 2,
    "remove_bbound": 3,
    "show_prefs": 4,
    "remove_prefs": 5,
    "to_main": 6,
    "set_order": 7,
    "set_desc": 8,
    "set_asc": 9,
  }

  code = ''

  if data["query_type"] == "settings":
    code += '0;'
    code += str(setting_types[data["type"]])

  elif data["query_type"] == "search":
    code += '1;'  # query_type
    code += convert_integer(data["offset"]) + ';'  # offset
    code += ('0' if data["type"] == "all" else '1') + ';'  # type
    code += data["regexp"]  # regexp
  
  elif data["query_type"] == "card":
    code += '2;'
    code += convert_integer(data["id"])

    if data.get("offset") != None:
      code += ';' + convert_integer(data["offset"]) + ';'
      code += data["regexp"]
  
  return code


def decoder(code: str) -> dict:
  data = {}
  setting_types = [
    "set_tbound",
    "remove_tbound",
    "set_bbound",
    "remove_bbound",
    "show_prefs",
    "remove_prefs",
    "to_main",
    "set_order",
    "set_desc",
    "set_asc",
  ]

  items = code.split(';')

  if items[0] == '0':  # settings
    data["query_type"] = "settings"
    data["type"] = setting_types[int(items[1])]
  
  elif items[0] == '1':  # search
    data["query_type"] = "search"
    data["offset"] = int(items[1], 36)
    data["type"] = "all" if items[2] == '0' else "part"
    data["regexp"] = ';'.join(items[3:])

  elif items[0] == '2':  # card
    data["query_type"] = "card"
    data["id"] = int(items[1], 36)

    if len(items) > 2:
      data["offset"] = int(items[2], 36)
      data["regexp"] = ';'.join(items[3:])

  return data