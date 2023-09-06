from asyncpg import Connection
from database import get_conn


async def add_user(user_id, username, firstname, inviter_id):
    conn: Connection = await get_conn()
    row = await conn.fetchrow(
        "INSERT INTO users(user_id, username, firstname, inviter_id) VALUES ($1, $2, $3, $4) RETURNING *",
        user_id, username, firstname, inviter_id)
    await conn.close()
    return row


async def get_users():
    conn: Connection = await get_conn()
    rows = await conn.fetch("SELECT * from users")
    await conn.close()
    return rows


async def get_user(user_id):
    conn: Connection = await get_conn()
    row = await conn.fetchrow("SELECT * from users WHERE user_id = $1", user_id)
    await conn.close()
    return row


async def update_user_balance(user_id, balance_diff):
    conn: Connection = await get_conn()
    await conn.execute("UPDATE users SET balance = round(balance + $2, 2) WHERE user_id = $1", user_id, balance_diff)
    await conn.close()


async def set_is_banned(user_id, status):
    conn: Connection = await get_conn()
    await conn.execute("UPDATE users SET is_banned = $2 WHERE user_id = $1", user_id, status)
    await conn.close()


async def set_is_wireguard_active(user_id, status):
    conn: Connection = await get_conn()
    await conn.execute("UPDATE users SET is_wireguard_active = $2 WHERE user_id = $1", user_id, status)
    await conn.close()


async def delete_user(user_id):
    conn: Connection = await get_conn()
    await conn.execute("DELETE FROM devices WHERE user_id = $1", user_id)
    await conn.execute("DELETE FROM history WHERE user_id = $1", user_id)
    await conn.execute("DELETE FROM users WHERE user_id = $1", user_id)
    await conn.close()
