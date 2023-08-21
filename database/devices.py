import asyncpg
from asyncpg import Connection
from asyncpg.exceptions import *
from config_parser import DB
from database import get_conn


async def get_devices_by_user_id(user_id):
    conn: Connection = await get_conn()
    rows = await conn.fetch("SELECT * FROM devices WHERE user_id = $1", user_id)
    return rows


async def add_new_device(user_id, device_type, name, server_id):
    conn: Connection = await get_conn()
    device_id = await conn.fetchval(
        "INSERT INTO devices(user_id, device_type, name, server_id) VALUES ($1, $2, $3, $4) RETURNING device_id",
        user_id, device_type, name, server_id)
    await conn.close()
    return device_id
