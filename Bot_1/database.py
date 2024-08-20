import sqlite3


conn = sqlite3.connect('database.db')
c = conn.cursor()

def initiate_db():
    c.execute('''CREATE TABLE IF NOT EXISTS Products
                (id INTEGER PRIMARY KEY, title TEXT NOT NULL, description TEXT, price INTEGER NOT NULL, photo TEXT)''')
    conn.commit()

    c.execute('''CREATE TABLE IF NOT EXISTS Users
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      username TEXT NOT NULL,
                      email TEXT NOT NULL,
                      age INTEGER NOT NULL,
                      balance INTEGER NOT NULL)''')
    conn.commit()


def get_all_products():
    c.execute("SELECT * FROM Products")
    products = c.fetchall()
    conn.commit()
    return products


def get_product_by_id(product_id):
    c.execute("SELECT title, price FROM products WHERE id = ?", (product_id,))
    product_info = c.fetchone()
    conn.commit()
    return product_info


def add_user(user):
    # Добавляем нового пользователя
    c.execute("INSERT INTO Users (user_id, username, email, phone, sity, address) VALUES (?, ?, ?, ?, ?, ?)",
    (user.user_id, user.username, user.email, user.phone, user.sity, user.address))
    conn.commit()


def get_user_by_id(user_id):
    c.execute("SELECT * FROM Users WHERE user_id = ?", (user_id,))
    user = c.fetchone()
    conn.commit()
    return user


def is_included(user_id):
    # Проверяем, есть ли пользователь с таким именем в таблице
    c.execute("SELECT COUNT(*) FROM Users WHERE user_id = ?", (user_id,))
    count = c.fetchone()[0]
    conn.commit()
    return count > 0


