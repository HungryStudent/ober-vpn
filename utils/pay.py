from yookassa import Configuration, Payment
from yookassa.domain.response import PaymentResponse

from config_parser import YOOKASSA_TOKEN, YOOKASSA_SHOP_ID, BOT_NAME

Configuration.configure(YOOKASSA_SHOP_ID, YOOKASSA_TOKEN)


def create_payment(amount, user_id) -> PaymentResponse:
    payment = Payment.create({
        "amount": {
            "value": amount,
            "currency": "RUB"
        },
        "capture": True,
        "payment_method_data": {
            "type": "bank_card"
        },
        "confirmation": {
            "type": "redirect",
            "return_url": f"https://t.me/{BOT_NAME}"
        },
        "description": f"Пополнение баланса",
        "metadata": {"user_id": user_id}
    })
    return payment