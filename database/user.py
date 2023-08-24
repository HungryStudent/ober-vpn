import asyncpg
from asyncpg import Connection
from asyncpg.exceptions import *
from config_parser import DB
from database import get_conn


async def add_user(user_id, username, firstname, inviter_id):
    conn: Connection = await get_conn()
    await conn.execute(
        "INSERT INTO users(user_id, username, firstname, inviter_id) VALUES ($1, $2, $3, $4)",
        user_id, username, firstname, inviter_id)
    await conn.close()


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
    await conn.execute("UPDATE users SET balance = balance + $2 WHERE user_id = $1", user_id, balance_diff)


async def set_is_banned(user_id, status):
    conn: Connection = await get_conn()
    await conn.execute("UPDATE users SET is_banned = $2 WHERE user_id = $1", user_id, status)
