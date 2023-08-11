import asyncpg
from asyncpg import Connection

from config_parser import DB


async def get_conn() -> Connection:
    return await asyncpg.connect(user=DB.user, password=DB.password, database=DB.database, host=DB.host)
