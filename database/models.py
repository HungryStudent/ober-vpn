from asyncpg import Connection
from database import get_conn


async def create_models():
    conn: Connection = await get_conn()
    await conn.execute("CREATE TABLE IF NOT EXISTS users("
                       "user_id BIGINT PRIMARY KEY,"
                       "username VARCHAR(32),"
                       "firstname VARCHAR(64),"
                       "reg_time TIMESTAMP)")
    await conn.execute("CREATE TABLE IF NOT EXISTS countries("
                       "country_id SMALLSERIAL PRIMARY KEY,"
                       "name VARCHAR(32))")
    await conn.execute("CREATE TABLE IF NOT EXISTS servers("
                       "server_id SMALLSERIAL PRIMARY KEY,"
                       "ip_address VARCHAR(15),"
                       "server_password VARCHAR(100),"
                       "outline_url VARCHAR(64),"
                       "outline_sha VARCHAR(64),"
                       "country_id SMALLINT REFERENCES countries (country_id),"
                       "is_current BOOLEAN DEFAULT FALSE)")

    await conn.close()
