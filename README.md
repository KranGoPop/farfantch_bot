# Farfetch Parser

Добро пожаловать в Farfetch Parser! Этот бот создан для парсинга известного сайта [farfetch.com](https://www.farfetch.com/). Он извлекает цену, фотографию и название разнообразных моделей кросовок. Проект работает на технологиях MySQL, docker-compose и python-telegram-bot.

## Начало работы

Для легкого старта убедитесь, что у вас установлены необходимые инструменты: [Docker](https://www.docker.com/) и [docker-compose](https://docs.docker.com/compose/). Запустите программу можно с помощью следующей команды:

```bash
./build.sh
```

Аргумент `-r` перезаписывает данные с последними предложениями на farfetch.com.

## Конфигурация

Укажите токен для вашего телеграм-бота в файле `config.env`. Установите токен в качестве значения переменной окружения `BOT_TOKEN`.

```plaintext
BOT_TOKEN=your_telegram_bot_token
```

Без указания токена программа выполнит только парсинг и запись в БД данных с farfetch.com без отправки в Telegram.

## Получение токена для Telegram бота

1. Обратитесь к боту [@BotFather](https://t.me/BotFather).
2. Создайте нового бота.
3. Для удобства можете добавить в [@BotFather](https://t.me/BotFather) команду `settings`. Вбивая `/settings` в бота можно получить доступ к настройкам бота.
