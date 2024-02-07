"""

"docker run -p 6379:6379 --name my-redis redis" первичный запуск Redis

"docker start my-redis" старт Redis

"celery -A megano worker --loglevel=info" запуск Celery worker

отправка задач для Celery:
from .celery import app, buy_milk
task1 = buy_milk.delay(7)

"""
