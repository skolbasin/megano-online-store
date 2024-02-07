#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import subprocess
import sys
from multiprocessing import Process

from megano.settings import CELERY_ON


def main():
    """Run administrative tasks."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "megano.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


def celery_start():
    subprocess.call(
        ["celery", "-A", "megano", "worker", "--loglevel=info"],
        stdout=subprocess.PIPE,
        text=True,
    )


if __name__ == "__main__":
    if not CELERY_ON:
        main()
    else:
        subprocess.call(
            ["docker", "run", "-p", "6379:6379", "--name", "my-redis", "redis"],
            stdout=subprocess.PIPE,
            text=True,
        )
        subprocess.call(
            [
                "docker",
                "start",
                "my-redis",
            ],
            stdout=subprocess.PIPE,
            text=True,
        )
        main_process = Process(target=main)
        celery_process = Process(target=celery_start)
        main_process.start()
        celery_process.start()
        main_process.join()
        celery_process.join()
