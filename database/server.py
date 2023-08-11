import asyncpg
from asyncpg import Connection
from asyncpg.exceptions import *
from config_parser import DB
from database import get_conn


async def set_default_server(country_id, server_id):
    conn: Connection = await get_conn()
    await conn.execute("UPDATE servers SET is_current = FALSE WHERE country_id = $1", country_id)
    await conn.execute("UPDATE servers SET is_current = TRUE WHERE server_id = $1", server_id)


async def get_servers_by_country_id(country_id):
    conn: Connection = await get_conn()
    rows = await conn.fetch("SELECT * from servers WHERE country_id = $1", country_id)
    await conn.close()
    return rows


async def add_server(name):
    conn: Connection = await get_conn()
    country_id = await conn.fetchval(
        "INSERT INTO countries(name) VALUES ($1) RETURNING country_id", name)
    await conn.close()
    return country_id


async def get_servers():
    conn: Connection = await get_conn()
    rows = await conn.fetch("SELECT * from servers")
    await conn.close()
    return rows


async def get_server(server_id):
    conn: Connection = await get_conn()
    row = await conn.fetchrow("SELECT * from servers WHERE server_id = $1", server_id)
    await conn.close()
    return row
