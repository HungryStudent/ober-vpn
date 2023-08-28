import uvicorn
from fastapi import FastAPI, Request

import database as db
from create_bot import bot
from utils.devices import check_wireguard_active

app = FastAPI()


@app.post('/api/pay/yookassa')
async def yookassa_request(request: Request):
    data = await request.json()
    amount = int(float(data["object"]["amount"]["value"]))
    user_id = int(float(data["object"]["metadata"]["user_id"]))
    await db.update_user_balance(user_id, amount)
    await db.add_history_record(user_id, amount, "Пополнение")
    await bot.send_message(user_id, f"Платеж проведен. На ваш аккаунт зачислено {amount}₽")
    await check_wireguard_active(call.from_user.id, call.bot)
    return 200


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
