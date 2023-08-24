from asyncpg import Connection
from database import get_conn


async def set_default_server(country_id, server_id):
    conn: Connection = await get_conn()
    await conn.execute("UPDATE servers SET is_current = FALSE WHERE country_id = $1", country_id)
    await conn.execute("UPDATE servers SET is_current = TRUE WHERE server_id = $1", server_id)
    await conn.close()


async def get_servers_by_country_id(country_id):
    conn: Connection = await get_conn()
    rows = await conn.fetch("SELECT * from servers WHERE country_id = $1", country_id)
    await conn.close()
    return rows


async def add_server(ip_address, server_password, outline_url, outline_sha, country_id):
    conn: Connection = await get_conn()
    server = await conn.fetchrow(
        "INSERT INTO servers(ip_address, server_password, outline_url, outline_sha, country_id)"
        "VALUES ($1, $2, $3, $4, $5) RETURNING *",
        ip_address, server_password, outline_url, outline_sha, country_id
    )
    await conn.close()
    return server


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


async def change_server_password(server_id, password):
    conn: Connection = await get_conn()
    await conn.execute("UPDATE servers SET password = $1 WHERE server_id = $2", password, server_id)
    await conn.close()


async def get_current_server_by_country_id(country_id):
    conn: Connection = await get_conn()
    row = await conn.fetchrow("SELECT * from servers WHERE country_id = $1 and is_current = TRUE", country_id)
    await conn.close()
    return row