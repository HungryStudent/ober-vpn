from asyncpg import Connection
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


async def get_countries_for_new_device():
    conn: Connection = await get_conn()
    rows = await conn.fetch(
        "SELECT * from countries JOIN servers s on countries.country_id = s.country_id WHERE s.is_current = TRUE "
        "and countries.is_hidden = FALSE")
    await conn.close()
    return rows


async def change_country_name(country_id, name):
    conn: Connection = await get_conn()
    await conn.execute("UPDATE countries SET name = $1 WHERE country_id = $2", name, country_id)
    await conn.close()


async def set_is_hidden(country_id, status):
    conn: Connection = await get_conn()
    await conn.execute("UPDATE countries SET is_hidden = $2 WHERE country_id = $1", country_id, status)
    await conn.close()


async def delete_country(country_id):
    conn: Connection = await get_conn()
    await conn.execute("DELETE FROM countries WHERE country_id = $1", country_id)
    await conn.close()
