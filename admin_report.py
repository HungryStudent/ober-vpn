import asyncio
import time

import database as db
from config_parser import ADMINS
from create_bot import bot
from utils import devices


# async def get_stats_data(stats):
#     users = await db.get_users()
#
#     return {"all_active": all_active, "all_inactive": all_inactive,
#             "wg_active": wg_active, "wg_no_config": wg_no_config, "wg_no_money": wg_no_money,
#             "ol_active": ol_active, "ol_no_config": ol_no_config, "ol_no_limit": ol_no_limit}


async def main():
    start = time.time()
    users = await db.get_users()
    today_users = await db.get_today_users()
    if today_users is None:
        today_users = []
    msg = f"""Общее количество клиентов - {len(users)}
Количество клиентов пришедших за день - {len(today_users)}\n\n"""
    all_active = 0
    all_inactive = 0
    wg_active = 0
    wg_no_config = 0
    wg_no_money = 0
    ol_active = 0
    ol_no_config = 0
    ol_no_limit = 0
    for user in users:
        stats = await devices.get_stats_for_menu(user)
        if stats["wireguard_status"] == "активен" or stats["outline_status"] == "активен":
            all_active += 1
            if stats["wireguard_status"] == "активен":
                wg_active += 1
            if stats["outline_status"] == "активен":
                ol_active += 1
        elif stats["wireguard_status"] == "не активен" and stats["outline_status"] == "не активен":
            all_inactive += 1
            if stats["wireguard_desc"] == "(нет конфигов)":
                wg_no_config += 1
            elif stats["wireguard_desc"] == "(недостаточно средств)":
                wg_no_money += 1

            if stats["outline_desc"] == "(нет ключей)":
                ol_no_config += 1
            elif stats["outline_desc"] == "(закончился трафик)":
                ol_no_limit += 1
    msg += f"""Активные/Неактивные - {all_active}/{all_inactive}

WG акт/нет конф/нет средств {wg_active}/{wg_no_config}/{wg_no_money}

OL акт/нет ключей/нет трафика {ol_active}/{ol_no_config}/{ol_no_limit}\n\n"""
    print(time.time() - start)
    countries = await db.get_countries()
    for country in countries:
        users = await db.get_users_by_country_id(country["country_id"])
        today_users = await db.get_today_users_by_country_id(country["country_id"])

        msg += f"""{country["name"]}:
        
Общее количество клиентов - {len(users)}
Количество клиентов пришедших за день - {len(today_users)}\n\n"""
        all_active = 0
        all_inactive = 0
        wg_active = 0
        wg_no_config = 0
        wg_no_money = 0
        ol_active = 0
        ol_no_config = 0
        ol_no_limit = 0
        for user in users:
            stats = await devices.get_stats_by_country(user, country["country_id"])
            if stats["wireguard_status"] == "активен" or stats["outline_status"] == "активен":
                all_active += 1
                if stats["wireguard_status"] == "активен":
                    wg_active += 1
                if stats["outline_status"] == "активен":
                    ol_active += 1
            elif stats["wireguard_status"] == "не активен" and stats["outline_status"] == "не активен":
                all_inactive += 1
                if stats["wireguard_desc"] == "(нет конфигов)":
                    wg_no_config += 1
                elif stats["wireguard_desc"] == "(недостаточно средств)":
                    wg_no_money += 1

                if stats["outline_desc"] == "(нет ключей)":
                    ol_no_config += 1
                elif stats["outline_desc"] == "(закончился трафик)":
                    ol_no_limit += 1
        msg += f"""WG акт/нет конф/нет средств {wg_active}/{wg_no_config}/{wg_no_money}

OL акт/нет ключей/нет трафика {ol_active}/{ol_no_config}/{ol_no_limit}\n\n"""
    print(time.time() - start)
    for admin in ADMINS:
        await bot.send_message(admin, msg)
    session = await bot.get_session()
    await session.close()


if __name__ == '__main__':
    asyncio.run(main())
