# Telegram-бот.
Telegram-бот, который обращается к API сервиса Практикум.Домашка и узнавает
статус вашей домашней работы: взята ли ваша домашка в ревью, проверена ли она,
а если проверена — то принял её ревьюер или вернул на доработку.

## Технологии
* Python3
* Python-telegram-bot 13.7
## Установка
Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/Oorzhakau/homework_bot.git
cd homework_bot
```

Cоздать и активировать виртуальное окружение:

```
python3 -m venv venv
source venv/bin/activate
```

Установить зависимости из файла requirements.txt:

```
python3 -m pip install --upgrade pip
pip install -r requirements.txt
```
Создать файл .env в корне директории и внести в нее следующие переменные окружения:
```
PRACTICUM_TOKEN = <[Токен Практикум.Домашка](https://oauth.yandex.ru/authorize?
response_type=token&client_id=1d0b9dd4d652455a9eb710d450ff456a)>
TELEGRAM_TOKEN = <[Токен телеграмм-бота](https://core.telegram.org/bots#6-botfather)>
TELEGRAM_CHAT_ID = <Ваш telegram id>
```
<details><summary>Help про ваш telegram id</summary>
    <i>Ваш telegram id можно узнать у бота @userinfobot</i>
</details>

Запустить проект:

```
python3 homework.py
```

## Список исполнителей
[Александр Ооржак](https://github.com/Oorzhakau)
