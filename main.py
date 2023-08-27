from manage_db import GroceriesDB
from scrape_products import ShopScraper


def main():
    try:
        # Initialise database
        db = GroceriesDB()

        # Initialise web driver
        scraper = ShopScraper()

        # Get Tesco products
        shop_ids = db.get_shop_ids()
        product_list = scraper.scrape("Tesco", shop_ids.get("Tesco"))
        # product_list = scraper.scrape("Ocado", shop_ids.get("Ocado"))

        # Insert to Product table
        db.insert_products(product_list)
    except Exception as err:
        print("Error", err)
    finally:
        # Close db and web driver
        db.close()
        scraper.close()


if __name__ == "__main__":
    main()
