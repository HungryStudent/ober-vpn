from asyncpg import Connection
from database import get_conn


async def get_devices_by_user_id(user_id):
    conn: Connection = await get_conn()
    rows = await conn.fetch("SELECT * FROM devices WHERE user_id = $1", user_id)
    return rows


async def get_devices_by_user_id_and_device_type(user_id, device_type):
    conn: Connection = await get_conn()
    rows = await conn.fetch("SELECT * FROM devices WHERE user_id = $1 AND device_type = $2", user_id, device_type)
    return rows


async def add_new_device(user_id, device_type, name, server_id):
    conn: Connection = await get_conn()
    device_id = await conn.fetchval(
        "INSERT INTO devices(user_id, device_type, name, server_id) VALUES ($1, $2, $3, $4) RETURNING device_id",
        user_id, device_type, name, server_id)
    await conn.close()
    return device_id


async def set_outline_id(device_id, outline_id):
    conn: Connection = await get_conn()
    await conn.execute("UPDATE devices SET outline_id = $2 WHERE device_id = $1", device_id, outline_id)


async def delete_device(device_id):
    conn: Connection = await get_conn()
    await conn.execute("DELETE FROM devices WHERE device_id = $1", device_id)


async def get_device(device_id):
    conn: Connection = await get_conn()
    row = await conn.fetchrow("SELECT * FROM devices WHERE device_id = $1", device_id)
    return row
