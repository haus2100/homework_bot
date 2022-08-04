# homework_bot

Телеграмбот для проверки статуса домашней работы на Яндекс.Практикуме:
- запрашивает статус работы через api яндекс.практикума;
- посылает статус в указанный телеграм;
- токены защищены и добавляются через переменные окружения;
- есть логгер;
- обрабатывает исключения.

## Применяемые технологии и библиотеки:

- Python 3.9.6
- python-telegram-bot 13.7.
- python-dotenv 0.19.0
- requests 2.26.0

## Требование к запуску проекта

У вас должен быть доступ к api Яндекс.Практикума.

## Как запустить проект:

__На автономном сервере windows:__

_Клонировать репозиторий и перейти в него в командной строке:_
```
git clone https://github.com/haus2100/homework_bot.git
```
```
cd homework_bot
```

_Cоздать и активировать виртуальное окружение:_
```
python -m venv venv
```
```
source venv/Scripts/activate
```

_Установить зависимости из файла requirements.txt:_
```
python -m pip install --upgrade pip
```
```
pip install -r requirements.txt
```

_Создать в репозитории файл .env с токеном вашего бота в формате:_
```
PRACTICUM_TOKEN = '<ваш токен для доступа к Яндекс.Практикуму>'
TELEGRAM_TOKEN = '<Ваш токен для управления ботом>'
TELEGRAM_CHAT_ID = '<id вашего аккаунта в телеграме>'
```
__или__

_В консоли экспортируйте в виртуальное окружение токены для вашего Телеграм бота:_
```
export PRACTICUM_TOKEN = '<ваш токен для доступа к Яндекс.Практикуму>'
export TELEGRAM_TOKEN = '<Ваш токен для управления ботом>'
export TELEGRAM_CHAT_ID = '<id вашего аккаунта в телеграме>'
```

_Запустите проект:_
```
python homework.py
```

_По завершению работы деактивируйте виртуальное окружение командой:_
```
deactivate
```
