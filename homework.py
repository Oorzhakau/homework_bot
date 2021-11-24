"""
Telegram-бот, который обращается к API сервиса Практикум.Домашка и узнавает
статус вашей домашней работы: взята ли ваша домашка в ревью, проверена ли она,
а если проверена — то принял её ревьюер или вернул на доработку.
"""
from typing import Optional
import logging
import os
import sys
import time
from exceptions import (EndpointError, InvalidResponse, InvalidStatusCode,
                        KeyNotFind, VariableNotDefined)

import requests

import telegram
from dotenv import load_dotenv

load_dotenv()


PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}

logging.basicConfig(
    format='%(asctime)s [%(levelname)s] %(message)s',
    level=logging.DEBUG,
    handlers=[logging.StreamHandler(stream=sys.stdout)]
)


def send_message(bot: telegram.Bot, message: str) -> None:
    """
    Функция отправляет сообщение в Telegram чат, определяемый переменной
    окружения TELEGRAM_CHAT_ID.

    Параметры:
    bot (telegram.Bot) - бот, осуществляющий отправку сообщения
    message (str) - Сообщение

    Возвращает:
    None.
    """
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logging.info(f"Бот отправил сообщение \"{message}\"")
    except telegram.e as error:
        logging.error(f'Ошибка при отправки сообщения: {error}')


def get_api_answer(current_timestamp: int) -> dict:
    """
    Функция делает запрос к единственному эндпоинту API-сервиса
    Практикум.Домашка.

    Параметры:
    current_timestamp (int) - временная метка

    Возвращает:
    dict - ответ сервера.
    """
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    response = requests.get(ENDPOINT, headers=HEADERS, params=params)
    if response.status_code != 200:
        raise InvalidStatusCode(f"Ошибка сервера. Статус -"
                                f"{response.status_code}")
    response = response.json()
    return response


def check_response(response: Optional[dict]) -> Optional[list]:
    """
    Функция проверяет ответ API на корректность.

    Параметры:
    response (dict) - ответ сервера

    Возвращает:
    list - список домашних работ.
    """

    if not isinstance(response, dict):
        raise InvalidResponse("Ответ не приведен к типу dict")
    if response.get("error"):
        raise EndpointError(response["error"]["error"])
    if "homeworks" not in response.keys():
        raise KeyNotFind("В переданном ответе отсутствует"
                         " атрибут \"homeworks\"")
    if not isinstance(response.get('homeworks'), list):
        raise InvalidResponse("Ответ не должен быть типа list")
    logging.debug("Корректный ответ от сервера получен.")
    return response.get('homeworks')


def parse_status(homework: dict) -> str:
    """
    Функция извлекает из информации о конкретной домашней работе
    статус этой работы.

    Параметры:

    Возвращает:
    str - сообщение о статусе домашней работы.
    """
    homework_name = homework.get('homework_name')
    homework_status = homework.get('status')
    if ('homework_name' not in homework.keys()):
        raise KeyNotFind("В переданном элементе отсутствует"
                         " атрибут \"homework_name\"")
    if ('status' not in homework.keys()):
        raise KeyNotFind("В переданном элементе отсутствует"
                         " атрибут \"status\"")
    if (homework_status not in HOMEWORK_STATUSES.keys()):
        raise KeyNotFind(f"Неизвестный статус работы: {homework_status}")
    verdict = HOMEWORK_STATUSES[homework_status]
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens() -> bool:
    """
    Функция проверяет доступность переменных окружения, которые
    необходимы для работы программы.

    Параметры:
    None

    Возвращает:
    bool - True если все переменные окружения заданы, иначе — False.
    """
    if PRACTICUM_TOKEN and TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
        logging.info("Переменные среды заданы.")
        return True
    return False


def main():
    """Основная логика работы бота."""
    try:
        if not check_tokens():
            raise VariableNotDefined()
    except VariableNotDefined:
        if not PRACTICUM_TOKEN:
            logging.critical("Отсутствует обязательная переменная окружения:"
                             " 'PRACTICUM_TOKEN'")
        elif not TELEGRAM_TOKEN:
            logging.critical("Отсутствует обязательная переменная окружения:"
                             " 'TELEGRAM_TOKEN'")
        else:
            logging.critical("Отсутствует обязательная переменная окружения:"
                             " 'TELEGRAM_CHAT_ID'")
        logging.critical("Программа принудительно остановлена.")
    else:
        bot = telegram.Bot(token=TELEGRAM_TOKEN)
        current_timestamp = int(time.time())
        while True:
            try:
                response = get_api_answer(current_timestamp)
                homeworks = check_response(response)
                if not homeworks:
                    logging.debug("Новые статусы отсутствуют.")
                for homework in homeworks:
                    send_message(bot, parse_status(homework))
                current_timestamp = int(time.time())
                time.sleep(RETRY_TIME)
            except Exception as error:
                message = f'Сбой в работе программы: {error}'
                logging.error(message)
                time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()
