import asyncpg
from asyncpg import Connection
from asyncpg.exceptions import *
from config_parser import DB
from database import get_conn


async def add_country(name):
    conn: Connection = await get_conn()
    country_id = await conn.fetchval(
        "INSERT INTO countries(name) VALUES ($1) RETURNING country_id", name)
    await conn.close()
    return country_id


async def get_countries():
    conn: Connection = await get_conn()
    rows = await conn.fetch("SELECT * from countries")
    await conn.close()
    return rows


async def get_country(country_id):
    conn: Connection = await get_conn()
    row = await conn.fetchrow("SELECT * from countries WHERE country_id = $1", country_id)
    await conn.close()
    return row
