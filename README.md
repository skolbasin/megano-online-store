# Интернет-магазин MEGANO

Проект представляет собой простую реализацию онлайнового торгового центра или, другими словами, интернет-магазина. Реализован с использованием библиотеки Django на языке python

## Установка


1. Клонируйте репозиторий: `git clone https://gitlab.skillbox.ru/kurator_skillbox/python_django_team32.git`
2. Перейдите в каталог проекта: `cd megano`
3. Установите зависимости: `pip install -r requirements.txt`


## Развертывание и настройка окружения

Для запуска требуется установленный Docker

Для удобства работы над проектом, рекомендуется использовать виртуальное окружение. Для этого выполните следующие команды:


1. Установите `virtualenv`, если он ещё не установлен: `pip install virtualenv`
2. Создайте виртуальное окружение: `virtualenv env`
3. Активируйте виртуальное окружение:
   - На Windows: `env\Scripts\activate`
   - На macOS и Linux: `source env/bin/activate`
4. Перейдите в каталог проекта: `cd Chat_with_Channels`
5. Создайте файл `.env`
6. Перенесите переменные окружения из образца `.env.example` в `.env`
7. Запустите сервер разработки: `python manage.py runserver`
8. Откройте браузер и перейдите по адресу: `http://127.0.0.1:8000/`


#  В приложении используется сервис Celery 

Запускается автоматически при CELERY_ON=1 (см. Переменные окружения), здесь происходит следующее:
1. Разворачивается Redis:

   docker run -p 6379:6379 --name my-redis redis
2. Запускается Celery:

   celery -A megano worker --loglevel=info

##  Переменные окружения (описание в файле .env.example):


DEBUG='' # Режим Debug: 1 или 0

CELERY_ON='' # Режим Celery 1 или 0

SECRET_KEY='' # Секретный код из settings

INTERNAL_IPS='' # Внутренние IPS

ALLOWED_HOSTS='' # Разрешенные хосты

CELERY_BROKER_URL = '' #  URL для брокера Celery

CELERY_RESULT_BACKEND = '' #  URL для бэкенда Celery

PRODUCT_CACHE_KEY = '' #  Ключ кэша продукта

