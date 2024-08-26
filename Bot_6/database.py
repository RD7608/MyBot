import aiosqlite
import logging

logger = logging.getLogger(__name__)


async def init_db():
    async with aiosqlite.connect('database.db') as db:
        await db.execute('''CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            name TEXT,
            email TEXT,
            registration_date TEXT,
            ban INTEGER DEFAULT 0)''')

        await db.execute('''CREATE TABLE IF NOT EXISTS users_ban (
            user_id INTEGER,
            event TEXT,
            date TEXT,
            reason TEXT,
            PRIMARY KEY (user_id, date))''')

        await db.execute(''' CREATE TABLE IF NOT EXISTS reminders (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            event_type TEXT,
            event_name TEXT,
            event_message TEXT,
            event_date TEXT,
            event_time TEXT,
            status INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users (user_id))''')
        await db.commit()


async def add_user(user_id, name, email, registration_date):
    async with aiosqlite.connect('database.db') as db:
        await db.execute('INSERT INTO users (user_id, name, email, registration_date) VALUES (?, ?, ?, ?)',
                         (user_id, name, email, registration_date))
        await db.commit()


async def get_user(user_id=None):
    if user_id is None:
        async with aiosqlite.connect('database.db') as db:
            async with db.execute('SELECT * FROM users') as cursor:
                return await cursor.fetchall()
    async with aiosqlite.connect('database.db') as db:
        async with db.execute('SELECT * FROM users WHERE user_id = ?', (user_id,)) as cursor:
            return await cursor.fetchone()


async def ban_user(user_id, reason, date):
    async with aiosqlite.connect('database.db') as db:
        await db.execute('UPDATE users SET ban = 1 WHERE user_id = ?', (user_id,))
        await db.execute('INSERT INTO users_ban (user_id, event, date, reason) VALUES (?, ?, ?, ?)',
                         (user_id, 'ban', date, reason))
        await db.commit()


async def unban_user(user_id, reason, date):
    async with aiosqlite.connect('database.db') as db:
        await db.execute('UPDATE users SET ban = 0 WHERE user_id = ?', (user_id,))
        await db.execute('INSERT INTO users_ban (user_id, event, date, reason) VALUES (?, ?, ?, ?)',
                         (user_id, 'unban', date, reason))
        await db.commit()


async def add_reminder(user_id, event_type, event_name, event_message, event_date, event_time):
    try:
        async with aiosqlite.connect('database.db') as db:
            await db.execute('INSERT INTO reminders (user_id, event_type, event_name, event_message, event_date, event_time) VALUES (?, ?, ?, ?, ?, ?)',
                             (user_id, event_type, event_name, event_message, event_date, event_time))
            await db.commit()
    except aiosqlite.Error as e:
        logging.error(f"Ошибка при создании напоминания для пользователя {user_id}: {e}")
        raise RuntimeError("Не удалось создать новое напоминание. Пожалуйста, попробуйте позже.") from e


async def get_reminders(user_id=None):
    if user_id is None:
        async with aiosqlite.connect('database.db') as db:
            async with db.execute('SELECT * FROM reminders') as cursor:
                return await cursor.fetchall()
    else:
        async with aiosqlite.connect('database.db') as db:
            async with db.execute('SELECT * FROM reminders WHERE user_id = ? AND status = 0', (user_id,)) as cursor:
                return await cursor.fetchall()


async def del_reminder(user_id, reminder_id):
    async with aiosqlite.connect('database.db') as db:
        cursor = await db.execute('DELETE FROM reminders WHERE user_id = ? AND id = ?', (user_id, reminder_id))
        await db.commit()
        rows_affected = cursor.rowcount
        return rows_affected > 0


async def del_all_reminders(user_id):
    async with aiosqlite.connect('database.db') as db:
        await db.execute('DELETE FROM reminders WHERE user_id = ?', (user_id,))
        await db.commit()


async def get_reminders_by_time(c_date, c_time):
    async with aiosqlite.connect('database.db') as db:
        cursor = await db.execute('SELECT * FROM reminders WHERE event_date = ? AND event_time = ? AND status = 0', (c_date, c_time))
        reminders = await cursor.fetchall()
        return reminders


async def set_reminder_status(rem_id, user_id, status):
    async with aiosqlite.connect('database.db') as db:
        cursor = await db.execute('UPDATE reminders SET status = ? WHERE id = ? AND user_id = ?', (status, rem_id, user_id,))
        await db.commit()
        rows_updated = cursor.rowcount
        return rows_updated
