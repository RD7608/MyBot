from datetime import date, datetime
import aiosqlite


async def get_reminders_by_time(c_date, c_time):
    print(c_date, c_time)
    async with aiosqlite.connect('database.db') as db:
        cursor = await db.execute('SELECT * FROM reminders WHERE event_date = ? AND event_time = ? AND status = 0',
                                  (c_date, c_time))
        reminders = await cursor.fetchall()
        print(reminders)
        return reminders



c_date = date.today()
c_time = datetime.now().strftime('%H:%M')
reminders = get_reminders_by_time(date.today(), datetime.now().strftime('%H:%M'))
print(reminders)
