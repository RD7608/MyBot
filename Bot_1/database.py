import sqlite3
import logging


logger = logging.getLogger(__name__)

conn = sqlite3.connect('database.db')
c = conn.cursor()


def initiate_db():
    c.execute('''CREATE TABLE IF NOT EXISTS Users 
                    (user_id INTEGER PRIMARY KEY NOT NULL,
                    username TEXT NOT NULL,
                    city_id INTEGER,
                    address TEXT,
                    phone TEXT,
                    email TEXT,
                    ban INTEGER DEFAULT 0,
                    FOREIGN KEY (city_id) REFERENCES cities (id))''')
    conn.commit()

    c.execute('''CREATE TABLE IF NOT EXISTS Products
                (id INTEGER PRIMARY KEY, title TEXT NOT NULL, description TEXT, photo TEXT)''')
    conn.commit()

    c.execute('''CREATE TABLE IF NOT EXISTS orders 
                (id INTEGER PRIMARY KEY,
                user_id INTEGER NOT NULL,
                status INTEGER  NOT NULL,
                delivery_date TEXT NOT NULL,
                delivery_time TEXT NOT NULL,
                delivery_address TEXT NOT NULL,
                order_number TEXT NOT NULL),
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES Users (user_id))''')
    conn.commit()

    c.execute('''CREATE TABLE IF NOT EXISTS order_items
            (id INTEGER PRIMARY KEY,
            order_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            price REAL NOT NULL,
            FOREIGN KEY (order_id) REFERENCES orders (id))''')

    # Создаем таблицу городов
    c.execute('''CREATE TABLE IF NOT EXISTS cities (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL)''')

    conn.commit()

# Создаем таблицу цен
    c.execute('''CREATE TABLE IF NOT EXISTS prices (
            id INTEGER PRIMARY KEY,
            product_id INTEGER NOT NULL,
            city_id INTEGER NOT NULL,
            price REAL NOT NULL,
            FOREIGN KEY (product_id) REFERENCES products (id),
            FOREIGN KEY (city_id) REFERENCES cities (id))''')
    conn.commit()


def get_cities():
    c.execute("SELECT * FROM Cities")
    cities = c.fetchall()
    conn.commit()
    return cities


def get_all_products(city_id):
    c.execute("""
        SELECT p.*, pr.price
        FROM Products p
        JOIN Prices pr ON p.id = pr.product_id
        WHERE pr.city_id = ?
    """, (city_id,))
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
    try:
        # Добавляем нового пользователя
        c.execute("INSERT INTO Users (user_id, username, email, phone, sity, address) VALUES (?, ?, ?, ?, ?, ?)",
                  (user.user_id, user.username, user.email, user.phone, user.sity, user.address))
        conn.commit()
        # Проверяем, что данные были добавлены в базу данных
        c.execute("SELECT * FROM Users WHERE user_id = ?", (user.user_id,))
        if c.fetchone():
            logger.info("Пользователь успешно добавлен в базу данных")
            return True
        else:
            logger.error("Данные пользователя не были добавлены в базу данных")
            return False
    except sqlite3.Error as e:
        logger.error(f"Ошибка: {e}")
        return False


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


# Функция для записи заказа в базу данных
def insert_order(user_id, delivery_date, delivery_time, delivery_address, order_number):
    c.execute('''INSERT INTO orders (user_id, status, delivery_date, delivery_time, delivery_address, order_number)
     VALUES (?, 1, ?, ?, ?, ?)''',
              (user_id, delivery_date, delivery_time, delivery_address, order_number))
    conn.commit()
    return c.lastrowid


# Функция для записи данных корзины в базу данных
def insert_order_item(order_id, product_id, quantity, price):
    c.execute('''
        INSERT INTO order_items (order_id, product_id, quantity, price)
        VALUES (?, ?, ?, ?)''',
              (order_id, product_id, quantity, price))
    conn.commit()


def get_orders(user_id):
    c.execute("SELECT * FROM Orders WHERE user_id = ?", (user_id,))
    orders = c.fetchall()
    conn.commit()
    return orders


def get_orders_by_status(user_id, status):
    status_map = {
        1: "new",
        2: "in_progress",
        3: "in_delivery",
        4: "completed"
    }
    c.execute("SELECT * FROM Orders WHERE user_id = ? AND status = ?", (user_id, status_map[status]))
    orders = c.fetchall()
    conn.commit()
    return orders


def check_block(id):
    s = c.execute("SELECT * FROM block; ").fetchall()
    conn.commit()
    return (id,) in s


def set_block(id):
    c.execute(f"INSERT INTO block VALUES({id}); ").fetchall()
    conn.commit()


def del_block(id):
    c.execute(f"DELETE FROM block WHERE id = {id}; ").fetchall()
    conn.commit()
