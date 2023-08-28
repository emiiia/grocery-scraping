from manage_db import GroceriesDB
from scrape_products import ShopScraper


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
        product_list = scraper.scrape_tesco(shop_ids.get("Tesco"))
        product_list += scraper.scrape_ocado(shop_ids.get("Ocado"))

        # Insert to Product table
        db.insert_products(product_list)
    except Exception as err:
        print("Error", err)
    finally:
        # Close db and web driver
        if db:
            db.close()

        if scraper:
            scraper.close()


if __name__ == "__main__":
    main()
