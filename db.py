from unittest import result

import asyncpg
import asyncio
from datetime import time


async def connect_db():
    conn = await asyncpg.connect(
        user='dava',
        password='',
        database='bot_db',
        host='localhost'
    )
    return conn

async def get_active_tasks():
    conn = await connect_db()
    rows = await conn.fetch("""
        SELECT * FROM tasks
        WHERE is_active = TRUE
                            """)
    await conn.close()
    return rows


async def add_task(chat_id, send_time):
    conn = await connect_db()

    await conn.execute("""
        INSERT INTO tasks (chat_id, send_time)
        VALUES ($1, $2)
        ON CONFLICT (chat_id)
        DO UPDATE SET
            send_time = EXCLUDED.send_time,
            is_active = TRUE
    """, chat_id, send_time)
    await conn.close()

async def deactivate_task(chat_id):
    conn = await connect_db()
    await conn.execute("""
    UPDATE tasks
    SET is_active = FALSE
    WHERE chat_id = $1
    """, chat_id)
    await conn.close()
    return result

async def test():
    await add_task(111111111, time(18,30))

    conn = await connect_db()
    rows = await conn.fetch('SELECT * FROM tasks;')
    print(rows)
    await conn.close()

asyncio.run(test())