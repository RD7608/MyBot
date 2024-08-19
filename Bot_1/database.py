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


def add_user(username, email, age):
    # Добавляем нового пользователя с балансом 1000
    c.execute("INSERT INTO Users (username, email, age, balance) VALUES (?, ?, ?, 1000)", (username, email, age))
    conn.commit()


def is_included(username):
    # Проверяем, есть ли пользователь с таким именем в таблице
    c.execute("SELECT COUNT(*) FROM Users WHERE username = ?", (username,))
    count = c.fetchone()[0]
    conn.commit()
    return count > 0


