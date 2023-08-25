from asyncpg import Connection
from database import get_conn


async def add_history_record(user_id, amount, msg):
    conn: Connection = await get_conn()
    await conn.execute(
        "INSERT INTO history(user_id, datetime, amount, msg) VALUES ($1, NOW(), $2, $3)",
        user_id, amount, msg)
    await conn.close()


async def get_history_by_user_id(user_id):
    conn: Connection = await get_conn()
    rows = await conn.fetch("SELECT * from history WHERE user_id = $1", user_id)
    await conn.close()
    return rows
