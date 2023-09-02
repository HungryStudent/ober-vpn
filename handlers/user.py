from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery
from tabulate import tabulate

import database as db
import keyboards.user as user_kb
import utils.devices
from config_parser import BOT_NAME, wireguard_price
from create_bot import dp

start_msgs = {"exists": """Приветствуем вас снова, {firstname}!

Баланс {balance}₽ (~{days} дней)
WireGuard {wireguard_status} ({wireguard_desc})
ГБ в Outline можно приобрести (списание разовое)
Если вы уже купили ГБ для Outline, ваш ключ останется 
активным, независимо от баланса.

При потере QR-кода или конфиг-файла, их можно снова 
скачать в разделе "Мои устройства".

<b>ВНИМАНИЕ!</b>
Если WireGuard заблокирован в вашем регионе, 
рекомендуем использовать Outline.

<b>Используя наш сервис, вы соглашаетесь с тем, что мы 
не несем ответственности за ваши действия в 
интернете!</b>

👭 Пригласите друзей и заработайте 50₽ за каждого, 
плюс каждый ваш друг получит 100₽ на баланс!""",

              "new": """Приветствуем Вас, <b>{firstname}</b>!

Подключите VPN бесплатно! Дарим вам 100₽ на баланс!

Высокая скорость
Свободный доступ к сайтам 
Удобная форма оплаты 
Невысокая стоимость 
Мы используем два типа VPN - WireGuard и Outline

⬇️⬇️⬇️ Жмите кнопку! ⬇️⬇️⬇️""",

              "new_invite": """"Привет, <b>{firstname}</b>!

Вас пригласил сюда {inviter_firstname}, поэтому он получил 50₽ на свой баланс!
А мы вам дарим 100₽ на баланс!

Высокая скорость
Свободный доступ к сайтам 
Удобная форма оплаты 
Невысокая стоимость
Мы используем два типа VPN - WireGuard и Outline

⬇️⬇️⬇️ Жмите кнопку! ⬇️⬇️⬇️"""}


@dp.message_handler(commands=['start'], state="*")
async def start_command(message: Message, state: FSMContext):
    await state.finish()
    user = await db.get_user(message.from_user.id)

    if user is None:
        kb = user_kb.start
        msg = start_msgs["new"].format(firstname=message.from_user.first_name)
        try:
            inviter_id = int(message.get_args())
        except ValueError:
            inviter_id = None
        else:
            if inviter_id == message.from_user.id:
                inviter_id = None
            else:
                inviter = await db.get_user(inviter_id)
                msg = start_msgs["new_invite"].format(firstname=message.from_user.first_name,
                                                      inviter_firstname=inviter["firstname"])
                await db.update_user_balance(inviter_id, 50)
                await db.add_history_record(inviter_id, 50, "Реферальный бонус")
        user = await db.add_user(message.from_user.id, message.from_user.username, message.from_user.first_name,
                                 inviter_id)
    else:
        menu_stats = await utils.devices.get_stats_for_menu(user)
        msg = start_msgs["exists"].format(firstname=message.from_user.first_name, balance=user["balance"],
                                          days=menu_stats["days"],
                                          wireguard_status=menu_stats["wireguard_status"],
                                          wireguard_desc=menu_stats["wireguard_desc"])
        kb = user_kb.menu

    await message.answer(msg, reply_markup=kb)


@dp.message_handler(state="*", text="Отмена")
async def cancel(message: Message, state: FSMContext):
    await state.finish()
    await message.answer("Ввод отменен", reply_markup=user_kb.menu)


@dp.callback_query_handler(text="show_menu", state="*")
async def show_menu(call: CallbackQuery, state: FSMContext):
    await state.finish()
    user = await db.get_user(call.from_user.id)
    menu_stats = await utils.devices.get_stats_for_menu(user)
    msg = start_msgs["exists"].format(firstname=call.from_user.first_name, balance=user["balance"],
                                      days=menu_stats["days"],
                                      wireguard_status=menu_stats["wireguard_status"],
                                      wireguard_desc=menu_stats["wireguard_desc"])
    await call.message.answer(msg, reply_markup=user_kb.menu)
    await call.answer()


@dp.callback_query_handler(state="*", text="start_vpn")
async def start_vpn(call: CallbackQuery, state: FSMContext):
    await state.finish()
    await call.message.edit_text("""Поздравляем, Вы активировали аккаунт OberVPN, 100₽ у вас на балансе! 

Теперь давайте настроим Ваш VPN.""", reply_markup=user_kb.add_device)


@dp.callback_query_handler(text="cancel", state="*")
async def inline_cancel(call: CallbackQuery, state: FSMContext):
    await state.finish()
    await call.message.edit_text("Ввод отменен", reply_markup=user_kb.show_menu)
    await call.answer()


@dp.callback_query_handler(text="ref_menu")
async def ref_menu(call: CallbackQuery, state: FSMContext):
    await call.message.answer(f"""Пошлите другу ссылку:

https://t.me/{BOT_NAME}?start={call.from_user.id}

Когда ваш друг зайдет в наш бот по этой ссылке и создаст аккаунт, вы получите 50₽ на баланс!""",
                              reply_markup=user_kb.show_menu)
    await call.answer()


@dp.callback_query_handler(state="*", text="history")
async def history(call: CallbackQuery, state: FSMContext):
    history = await db.get_history_by_user_id(call.from_user.id)
    formatted_history = [
        {
            "datetime": row["datetime"],
            "amount": row["amount"],
            "msg": row["msg"]
        }
        for row in history]
    formatted_history.insert(0, {"datetime": "Дата", "amount": "₽", "msg": "ТИП"})
    await call.message.answer(
        f'<b>Статистика</b>\n\n<pre>{tabulate(formatted_history, tablefmt="jira", numalign="left")}</pre>',
        reply_markup=user_kb.show_menu)
    await call.answer()
