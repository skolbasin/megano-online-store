import random
import time

from celery import shared_task


@shared_task
def payment(card_number: int) -> tuple:
    time.sleep(1)
    if card_number // 2 != 0 and card_number % 10 != 0:
        return True, None
    else:
        payment_errors = [
            "Превышен лимит. Невозможно выполнить операцию по карте",
            "Недостаточно средств для проведения операции по карте",
            "Техническая ошибка. Невозможно выполнить операцию по карте",
            "Истек срок действия банковской карты.",
        ]
        payment_error = random.choice(payment_errors)
        return False, payment_error
