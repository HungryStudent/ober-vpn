from asyncpg import Connection

from database import get_conn


async def get_devices_by_user_id(user_id):
    conn: Connection = await get_conn()
    rows = await conn.fetch("SELECT * FROM devices WHERE user_id = $1", user_id)
    await conn.close()
    return rows


async def get_devices_with_expired_sub_time_and_has_auto_renewal():
    conn: Connection = await get_conn()
    rows = await conn.fetch("SELECT * FROM devices WHERE sub_time < NOW() and has_auto_renewal = True")
    await conn.close()
    return rows

async def get_devices_by_user_id_and_device_type(user_id, device_type):
    conn: Connection = await get_conn()
    rows = await conn.fetch("SELECT * FROM devices WHERE user_id = $1 AND device_type = $2", user_id, device_type)
    await conn.close()
    return rows


async def get_devices_by_user_id_and_device_type_and_country_id(user_id, device_type, country_id):
    conn: Connection = await get_conn()
    rows = await conn.fetch("SELECT * FROM devices "
                            "JOIN servers s on s.server_id = devices.server_id "
                            "WHERE user_id = $1 AND device_type = $2 and s.country_id = $3", user_id, device_type,
                            country_id)
    await conn.close()
    return rows


async def add_new_device(user_id, device_type, name, server_id, sub_time, product_id=None, outline_limit=None):
    conn: Connection = await get_conn()
    device_id = await conn.fetchval(
        "INSERT INTO devices(user_id, device_type, name, server_id, sub_time, product_id, outline_limit) "
        "VALUES ($1, $2, $3, $4, $5, $6, $7)"
        " RETURNING device_id",
        user_id, device_type, name, server_id, sub_time, product_id, outline_limit)
    await conn.close()
    return device_id


async def set_outline_id(device_id, outline_id):
    conn: Connection = await get_conn()
    await conn.execute("UPDATE devices SET outline_id = $2 WHERE device_id = $1", device_id, outline_id)
    await conn.close()

async def set_has_auto_renewal(device_id, status):
    conn: Connection = await get_conn()
    await conn.execute("UPDATE devices SET has_auto_renewal = $2 WHERE device_id = $1", device_id, status)
    await conn.close()

async def set_outline_limit(device_id, limit):
    conn: Connection = await get_conn()
    await conn.execute("UPDATE devices SET outline_limit = $2 WHERE device_id = $1", device_id, limit)
    await conn.close()

async def set_sub_time(device_id, sub_time):
    conn: Connection = await get_conn()
    await conn.execute("UPDATE devices SET sub_time = $2 WHERE device_id = $1", device_id, sub_time)
    await conn.close()


async def delete_device(device_id):
    conn: Connection = await get_conn()
    await conn.execute("DELETE FROM devices WHERE device_id = $1", device_id)
    await conn.close()


async def get_device(device_id):
    conn: Connection = await get_conn()
    row = await conn.fetchrow("SELECT * FROM devices WHERE device_id = $1", device_id)
    await conn.close()
    return row


async def get_devices_by_server_id(server_id):
    conn: Connection = await get_conn()
    rows = await conn.fetch("SELECT * FROM devices WHERE server_id = $1", server_id)
    await conn.close()
    return rows


async def get_wireguard_devices_for_payment(user_id):
    conn: Connection = await get_conn()
    rows = await conn.fetch("SELECT * FROM devices WHERE user_id = $1 and device_type = 'wireguard'"
                            "and (has_first_payment = True "
                            "or (has_first_payment = False and extract(epoch from NOW() - create_time)/3600 > 24))",
                            user_id)
    await conn.close()
    return rows


async def set_devices_has_first_payment(user_id):
    conn: Connection = await get_conn()
    await conn.execute("UPDATE devices SET has_first_payment = True where user_id = $1", user_id)
    await conn.close()
