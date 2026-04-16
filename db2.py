import aiosqlite
from datetime import time

# Название файла базы данных
DB_PATH = 'bot_db.db'

async def init_db():
    """Создает таблицу при запуске бота, если её нет"""
    # Мы открываем соединение прямо здесь
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                chat_id INTEGER PRIMARY KEY,
                send_time TEXT,
                is_active INTEGER DEFAULT 1
            )
        """)
        # Сохраняем изменения
        await db.commit()

async def get_active_tasks():
    """Получает список всех, кому нужно отправить сообщение"""
    async with aiosqlite.connect(DB_PATH) as db:
        # Эта строчка позволяет обращаться к колонкам по именам, а не по номерам
        db.row_factory = aiosqlite.Row

        async with db.execute("SELECT chat_id, send_time FROM tasks WHERE is_active = 1") as cursor:
            rows = await cursor.fetchall()

            result = []
            for row in rows:
                t_str = row['send_time']
                # Превращаем текст "18:30:00" обратно в объект времени Python
                h, m, s = map(int, t_str.split(':'))
                result.append({
                    'chat_id': row['chat_id'],
                    'send_time': time(h, m)
                })
            return result

async def add_task(chat_id, send_time):
    """Добавляет или обновляет время рассылки для пользователя"""
    async with aiosqlite.connect(DB_PATH) as db:
        # Превращаем время в текст для хранения
        time_str = send_time.strftime("%H:%M:%S")

        await db.execute("""
            INSERT INTO tasks (chat_id, send_time, is_active)
            VALUES (?, ?, 1)
            ON CONFLICT(chat_id) DO UPDATE SET
                send_time = excluded.send_time,
                is_active = 1
        """, (chat_id, time_str))
        await db.commit()

async def deactivate_task(chat_id):
    """Выключает рассылку для пользователя"""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("""
            UPDATE tasks
            SET is_active = 0
            WHERE chat_id = ?
        """, (chat_id,))
        await db.commit()
        # Возвращаем количество измененных строк (чтобы бот понял, была ли рассылка)
        return cursor.rowcount
