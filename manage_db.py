import sqlite3


class GroceriesDB(object):
    def __init__(self):
        self.conn = sqlite3.connect("groceries.db")
        self.conn.execute("pragma foreign_keys = on")
        self.conn.commit()
        self.cur = self.conn.cursor()
        self.shops = {"Tesco": 0, "Ocado": 1}
        self.create_tables()

    def query(self, arg):
        self.cur.execute(arg)
        self.conn.commit()
        return self.cur

    def insert_data(self, product_list):
        for product in product_list:
            self.cur.execute(
                """
                INSERT INTO product (
                    shop_id,
                    name,
                    price,
                    discounted_price,
                    rating,
                    featured,
                    vegetarian,
                    vegan,
                    in_stock
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    product["shop_id"],
                    product["name"],
                    product["price"],
                    product["discounted_price"],
                    product["rating"],
                    product["featured"],
                    product["vegetarian"],
                    product["vegan"],
                    product["in_stock"],
                ),
            )
        self.conn.commit()

    def create_tables(self):
        # Create shop table
        self.cur.execute(
            """
            CREATE TABLE IF NOT EXISTS shop (
                shop_id INTEGER PRIMARY KEY,
                name TEXT
            )
        """
        )

        # Create product table
        self.cur.execute(
            """
            CREATE TABLE IF NOT EXISTS product (
                product_id INTEGER PRIMARY KEY,
                shop_id INTEGER,
                name TEXT,
                price INTEGER,
                discounted_price INTEGER,
                rating INTEGER,
                featured INTEGER,
                vegetarian INTEGER,
                vegan INTEGER,
                in_stock INTEGER,
                FOREIGN KEY(shop_id) REFERENCES shop(shop_id)
                    
            )
        """
        )

        # Create brand table
        self.cur.execute(
            """
            CREATE TABLE IF NOT EXISTS brand (
                brand_id INTEGER PRIMARY KEY,
                product_id INTEGER,
                name TEXT,
                FOREIGN KEY(product_id) REFERENCES product(product_id)
            )
        """
        )

        # Insert shop data
        for shop_name in list(self.shops.keys()):
            self.cur.execute(
                """
                        INSERT INTO shop (name)
                        VALUES (?)
                    """,
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
