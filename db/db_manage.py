import sqlite3
from loguru import logger
from datetime import datetime

from db.errors import NoSuchUser

logger.add(f"logs/logs_{datetime.now()}.log", format="{time} | {level} | {message}", level="DEBUG",
           rotation="00:00", compression="zip")


class DataBase:
    def __init__(self, db_name):
        self.db_name = db_name
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()
        self.users_table = self.cursor.execute("CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY, name TEXT, " \
                                               "user_id INTEGER, balance REAL)")
        self.products_table = self.cursor.execute("CREATE TABLE IF NOT EXISTS products(id INTEGER PRIMARY KEY," \
                                                  "name TEXT, price REAL, count INTEGER, market TEXT)")
        self.conn.commit()

    def add_product(self, data):
        try:
            self.cursor.execute("SELECT * FROM products WHERE name=?", (data["name"],))
            if len(self.cursor.fetchall()) == 0:
                self.cursor.execute("INSERT INTO products (name, price, count, market) VALUES (?, ?, ?, ?)",
                                    (data["name"], data["price"], data["count"], data["market"]))
                self.conn.commit()
            else:
                return "Товар уже существует"
            return "Product added successfully"
        except Exception as error:
            logger.error(error)
            return "Something wrong"

    def add_user(self, data):
        try:
            try:
                self.cursor.execute("SELECT * FROM users WHERE user_id=?", (data["id"],))
                is_user_exist = True if len(self.cursor.fetchall()) > 0 else False
                if not is_user_exist:
                    raise NoSuchUser
            except NoSuchUser:
                self.cursor.execute("INSERT INTO users (name, user_id, balance) VALUES (?, ?, ?)",
                                    (data["name"], data["id"], data["balance"]))
                self.conn.commit()
                return "User added successfully"
        except Exception as error:
            logger.error(error)
            return "Something went wrong"

    def get_user_balance(self, user_id):
        try:
            self.cursor.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
            balance = self.cursor.fetchone()
            return balance[0]
        except Exception as error:
            logger.error(error)
            return "Something went wrong"

    def get_products(self):
        try:
            self.cursor.execute("SELECT name, price, count, market FROM products")
            products = self.cursor.fetchall()
            return products
        except Exception as error:
            logger.error(error)
            return "Something went wrong"

    def buy_product(self, data: dict, user_id):
        try:
            self.cursor.execute("SELECT * from products WHERE name = ?", (data["name"],))
            product = self.cursor.fetchone()
            self.cursor.execute("SELECT * from users WHERE user_id = ?", (user_id,))
            user = self.cursor.fetchone()
            if product[3] > data["count"]:
                new_count = product[3] - data["count"]
                user_balance = user[3] - data["count"] * product[2]
                if user_balance > 0:
                    self.cursor.execute("UPDATE products SET count = ? WHERE name = ?", (new_count, data["name"]))
                    self.cursor.execute("UPDATE users SET balance = ? WHERE id = ?", (user_balance, user_id))
                    self.conn.commit()
                    return "Покупка прошла успешно"
                else:
                    return "Недостаточно средств на балансе"
            elif product[3] == data["count"]:
                user_balance = user[3] - data["count"] * product[2]
                if user_balance > 0:
                    self.cursor.execute("DELETE FROM products WHERE name = ?", (data["name"]))
                    self.cursor.execute("UPDATE users SET balance = ? WHERE id = ?", (user_balance, user_id))
                    self.conn.commit()
                    return "Покупка прошла успешно"
                else:
                    return "Недостаточно средств на балансе"
            else:
                return "Неверное количество"
        except Exception as error:
            logger.error(error)
            return "Something went wrong"

    def get_product_price(self, data: dict):
        try:
            self.cursor.execute("SELECT * from products WHERE name = ?", (data["name"]))
            product = self.cursor.fetchone()
            return product[4]
        except Exception as error:
            logger.error(error)
            return "Something went wrong"

    def get_users(self):
        try:
            self.cursor.execute("SELECT user_id from users")
            users_id = self.cursor.fetchall()
            return users_id
        except Exception as error:
            logger.error(error)
            return "Something went wrong"

    def add_product_count(self, product_name, count):
        try:
            self.cursor.execute("SELECT count from products WHERE name = ?", (product_name,))
            product_count = self.cursor.fetchone()[0] + count
            self.cursor.execute("UPDATE products SET count = ? WHERE name = ?", (product_count, product_name))
            self.conn.commit()
            return "Successfully added"
        except Exception as error:
            logger.error(error)
            return "Something went wrong"

    def change_product_price(self, product_name, price):
        try:
            self.cursor.execute("UPDATE products SET price = ? WHERE name = ?", (price, product_name))
            self.conn.commit()
            return "Successfully updated"
        except Exception as error:
            logger.error(error)
            return "Something went wrong"

    def top_up_user_balance(self, user_id, price):
        try:
            self.cursor.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
            user_balance = self.cursor.fetchone()[0]
            self.cursor.execute("UPDATE users SET balance = ? WHERE user_id = ?", (user_balance + price, user_id))
            self.conn.commit()
            return "Balance updated"
        except Exception as error:
            logger.error(error)
            return "Something went wrong"

    def __str__(self):
        return f"{self.db_name}"

    def __del__(self):
        self.conn.close()
        return "Connection closed"
