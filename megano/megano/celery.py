# from __future__ import absolute_import
import os
import random

from celery import Celery, shared_task

# этот код скопирован с manage.py
# он установит модуль настроек по умолчанию Django для приложения 'celery'.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "megano.settings")

# здесь вы меняете имя
app = Celery("megano")

# Для получения настроек Django, связываем префикс "CELERY" с настройкой celery
app.config_from_object("django.conf:settings", namespace="CELERY")

# загрузка tasks.py в приложение django
app.autodiscover_tasks()
