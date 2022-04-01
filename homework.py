import time
import telegram
import sys
import logging
import os

import requests
from requests import RequestException
from dotenv import load_dotenv
from http import HTTPStatus


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


VERDICTS = {
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
        error_message = f'Сообщение не отправлено {error}'
        logger.error(error_message)
        raise Exception(error)


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
        logger.error(f'Ошибка, статус запроса {error}')
        raise Exception(error)
    if homework_statuses.status_code != HTTPStatus.OK:
        error_message = 'Ошибка Request'
        logger.error(error_message)
        raise RequestException(error_message)
    try:
        response = homework_statuses.json()
    except Exception as error:
        logger.error(f'Нет ожидаемого ответа сервера {error}')
        raise Exception(error)
    return response


def check_response(response):
    """
    Проверяет ответ API на корректность.
    В случае успеха, выводит список домашних работ.
    """
    if not isinstance(response, dict):
        error_message = 'Не верный тип ответа API'
        logger.error(error_message)
        raise TypeError(error_message)
    if 'homeworks' not in response:
        error_message = 'Ключ homeworks отсутствует'
        logger.error(error_message)
        raise KeyError(error_message)
    homeworks = response.get('homeworks')
    if not isinstance(homeworks, list):
        error_message = 'homeworks не является списком'
        logger.error(error_message)
        raise TypeError(error_message)
    if len(homeworks) == 0:
        error_message = 'Пустой список домашних работ'
        logger.error(error_message)
        raise ValueError(error_message)
    homework = homeworks[0]
    return homework


def parse_status(homework):
    """Возвращает статус домашней работы."""
    if 'homework_name' not in homework:
        error_message = 'Ключ homework_name отсутствует'
        logger.error(error_message)
        raise KeyError(error_message)
    if 'status' not in homework:
        error_message = 'Ключ status отсутствует'
        logger.error(error_message)
        raise KeyError(error_message)

    homework_name = homework.get('homework_name')
    homework_status = homework.get('status')

    if homework_name is None or homework_status is None:
        return 'Работа не сдана на проверку'
    if homework_status not in VERDICTS:
        error_message = 'Неизвестный статус домашней работы'
        logger.error(error_message)
        raise Exception(error_message)

    verdict = VERDICTS.get(homework_status)

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
        logger.error(error_message)
        raise Exception(error_message)

    current_timestamp = 1
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())

    while True:
        try:
            response = get_api_answer(current_timestamp)
            homework = check_response(response)

            if homework and len(homework):
                message = parse_status(homework[0])
                send_message(bot, message)
            else:
                logger.debug('Новых статусов - НЕТ')
            current_timestamp = response['current_date']

        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logger.exception(message)
            send_message(bot, message)
        time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()
