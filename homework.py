import time
import telegram
import sys
import logging
import os

import requests
from requests import RequestException
from dotenv import load_dotenv
from http import HTTPStatus

from logging.handlers import RotatingFileHandler

load_dotenv()

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
fileHandler = logging.FileHandler('homework.log')
fileHandler.setFormatter(formatter)
logger.addHandler(fileHandler)
streamHandler = logging.StreamHandler(sys.stdout)
streamHandler.setFormatter(formatter)
logger.addHandler(streamHandler)

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


def send_message(bot, message):
    """Отправляет сообщение в Телеграм."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logger.info('Сообщение отправлено')
    except Exception as error:
        logging.error(f'Сообщение не отправлено {error}')


def get_api_answer(current_timestamp):
    """Возвращаем ответ API, преобразовав его к типам данных Python."""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}

    try:
        homework_statuses = requests.get(
            ENDPOINT,
            headers=HEADERS,
            params=params
        )
    except requests.exceptions.RequestException as error:
        logging.error(f'Ошибка URL {error}')
        raise SystemExit(error)
    if homework_statuses.status_code != HTTPStatus.OK:
        error_message = 'Ошибка Request'
        logging.error(error_message)
        raise RequestException(error_message)
    try:
        response = homework_statuses.json()
    except Exception as error:
        logging.error(f'Нет ожидаемого ответа сервера {error}')
        raise Exception(error)
    return response


def check_response(response):
    """
    Проверяет ответ API на корректность.
    В случае успеха, выводит список домашних работ.
    """
    if not isinstance(response, dict):
        error_message = 'Не верный тип ответа API'
        logging.error(error_message)
        raise TypeError(error_message)
    if 'homeworks' not in response:
        error_message = 'Ключ homeworks отсутствует'
        logging.error(error_message)
        raise KeyError(error_message)
    homeworks = response.get('homeworks')
    if not isinstance(homeworks, list):
        error_message = 'homeworks не является списком'
        logging.error(error_message)
        raise TypeError(error_message)
    if len(homeworks) == 0:
        error_message = 'Пустой список домашних работ'
        logging.error(error_message)
        raise ValueError(error_message)
    homework = homeworks[0]
    return homework


def parse_status(homework):
    """Возвращает статус домашней работы."""
    if 'homework_name' not in homework:
        error_message = 'Ключ homework_name отсутствует'
        logging.error(error_message)
        raise KeyError(error_message)
    if 'status' not in homework:
        error_message = 'Ключ status отсутствует'
        logging.error(error_message)
        raise KeyError(error_message)

    homework_name = homework.get('homework_name')
    homework_status = homework.get('status')

    if homework_name is None or homework_status is None:
        return 'Работа не сдана на проверку'
    if homework_status not in HOMEWORK_STATUSES:
        error_message = 'Неизвестный статус домашней работы'
        logging.error(error_message)
        raise Exception(error_message)

    verdict = HOMEWORK_STATUSES.get(homework_status)

    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    """Проверяет доступность переменных окружения."""
    return not (
        not PRACTICUM_TOKEN
        or not TELEGRAM_TOKEN
        or not TELEGRAM_CHAT_ID
    )


def main():
    """Основная логика работы бота."""
    if not check_tokens():
        error_message = 'Токены недоступны'
        logging.error(error_message)
        raise Exception(error_message)

    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())

    while True:
        try:
            response = get_api_answer(current_timestamp)

            if response:
                homework = check_response(response)
                logger.info('Есть новости')
                message = parse_status(homework)
                send_message(bot, message)

            current_timestamp = response.get('current_date')
            time.sleep(RETRY_TIME)

        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logging.error(message)
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()
