from manage_db import GroceriesDB
from scrape_products import ShopScraper
import sys, os


def main():
    db = None
    scraper = None
    try:
        # Initialise database
        db = GroceriesDB()

        # Initialise web driver
        scraper = ShopScraper()

        # Get Tesco products
        shop_ids = db.get_shop_ids()
        product_list = scraper.scrape_tesco_brands(shop_ids.get("Tesco"))
        product_list += scraper.scrape_ocado_brands(shop_ids.get("Ocado"))

        # Insert to Product table
        db.insert_products(product_list)
    except Exception as err:
        print("Error", err)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
    finally:
        # Close db and web driver
        if db:
            db.close()

        if scraper:
            scraper.close()


if __name__ == "__main__":
    main()
