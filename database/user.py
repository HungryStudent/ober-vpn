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


async def get_today_users():
    conn: Connection = await get_conn()
    rows = await conn.fetch("SELECT * FROM users WHERE reg_time::date = NOW()::date")
    await conn.close()
    return rows


async def get_users_with_admin():
    conn: Connection = await get_conn()
    rows = await conn.fetch("SELECT * FROM users WHERE is_admin = TRUE")
    await conn.close()
    return rows


async def get_users_by_country_id(country_id):
    conn: Connection = await get_conn()
    rows = await conn.fetch("select distinct users.user_id, balance, is_wireguard_active from users "
                            "join devices d on users.user_id = d.user_id "
                            "join servers s on s.server_id = d.server_id "
                            "join countries c on c.country_id = s.country_id and c.country_id = $1", country_id)
    await conn.close()
    return rows


async def get_users_by_server_id(server_id):
    conn: Connection = await get_conn()
    rows = await conn.fetch("select distinct users.user_id, balance, is_wireguard_active from users "
                            "join devices d on users.user_id = d.user_id "
                            "join servers s on s.server_id = $1", server_id)
    await conn.close()
    return rows


async def get_today_users_by_country_id(country_id):
    conn: Connection = await get_conn()
    rows = await conn.fetch("select distinct users.user_id, balance, is_wireguard_active from users "
                            "join devices d on users.user_id = d.user_id "
                            "join servers s on s.server_id = d.server_id "
                            "join countries c on c.country_id = s.country_id and c.country_id = $1 "
                            "WHERE reg_time::date = NOW()::date", country_id)
    await conn.close()
    return rows


async def get_today_users_by_server_id(country_id):
    conn: Connection = await get_conn()
    rows = await conn.fetch("select distinct users.user_id, balance, is_wireguard_active from users "
                            "join devices d on users.user_id = d.user_id "
                            "join servers s on s.server_id = $1 "
                            "WHERE reg_time::date = NOW()::date", country_id)
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


async def set_has_free_outline(user_id, status):
    conn: Connection = await get_conn()
    await conn.execute("UPDATE users SET has_free_outline = $2 WHERE user_id = $1", user_id, status)
    await conn.close()


async def set_admin_status(user_id, status):
    conn: Connection = await get_conn()
    await conn.execute("UPDATE users SET is_admin = $2 WHERE user_id = $1", user_id, status)
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


async def get_referals_count(user_id):
    conn: Connection = await get_conn()
    row = await conn.fetchrow("SELECT COUNT(*) as refs_count from users WHERE inviter_id = $1", user_id)
    await conn.close()
    return row["refs_count"]
