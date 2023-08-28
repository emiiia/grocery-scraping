import sqlite3
import os


class GroceriesDB(object):
    def __init__(self):
        self.name = "groceries.db"
        # Remove existing db
        if os.path.exists(self.name):
            os.remove(self.name)
        # Create new db
        self.conn = sqlite3.connect(self.name)
        self.conn.execute("pragma foreign_keys = on")
        self.conn.commit()
        self.cur = self.conn.cursor()
        # Initialise shops dict
        self.shops = {"Tesco": 0, "Ocado": 1}
        self.create_tables()

    def insert_brand(self, brand_name):
        self.cur.execute(
            "INSERT OR IGNORE INTO Brand (name) VALUES (?);",
            (brand_name,),
        )
        self.conn.commit()

        # Return brand id
        self.cur.execute(
            "SELECT brand_id FROM Brand WHERE name = ?;",
            (brand_name,),
        )
        return self.cur.fetchone()[0]

    def insert_products(self, product_list):
        for product in product_list:
            # Create brand if not exists
            brand_id = self.insert_brand(product["brand"])

            self.cur.execute(
                """
                INSERT INTO Product (
                    name,
                    price,
                    promotion_price,
                    promotion,
                    rating,
                    featured,
                    vegetarian,
                    vegan,
                    in_stock,
                    brand_id,
                    shop_id
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    product["name"],
                    product["price"],
                    product["promotion_price"],
                    product["promotion"],
                    product["rating"],
                    product["featured"],
                    product["vegetarian"],
                    product["vegan"],
                    product["in_stock"],
                    brand_id,
                    product["shop_id"],
                ),
            )
        self.conn.commit()

    def create_tables(self):
        # Create shop table
        self.cur.execute(
            """
            CREATE TABLE IF NOT EXISTS Shop (
                shop_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE
            )
        """
        )

        # Create product table
        self.cur.execute(
            """
            CREATE TABLE IF NOT EXISTS Product (
                product_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                price REAL,
                promotion_price REAL,
                promotion TEXT,
                rating REAL,
                featured INTEGER,
                vegetarian INTEGER,
                vegan INTEGER,
                in_stock INTEGER,
                brand_id INTEGER,
                shop_id INTEGER,
                FOREIGN KEY(brand_id) REFERENCES Brand(brand_id),
                FOREIGN KEY(shop_id) REFERENCES Shop(shop_id)
                    
            )
        """
        )

        # Create brand table
        self.cur.execute(
            """
            CREATE TABLE IF NOT EXISTS Brand (
                brand_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                UNIQUE(name)
            )
        """
        )

        # Insert shop data
        for shop_name in list(self.shops.keys()):
            self.cur.execute(
                "INSERT INTO Shop (name) VALUES (?)",
                (shop_name,),
            )
            # Set the ID of the shop in dict
            self.shops[shop_name] = self.cur.lastrowid

        self.conn.commit()

    def get_shop_ids(self):
        return self.shops

    def close(self):
        """Close the database connection"""
        self.conn.close()
