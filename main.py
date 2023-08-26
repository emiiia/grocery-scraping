from manage_db import GroceriesDB
from scrape_products import ShopScraper

TESCO_CEREAL_URL = (
    "https://www.tesco.com/groceries/en-GB/shop/food-cupboard/cereals/all"
)
OCADO_CEREAL_URL = (
    "https://www.ocado.com/browse/food-cupboard-20424/breakfast-cereals-38715"
)


def main():
    try:
        # Initialise database
        db = GroceriesDB()

        # Initialise web driver
        scraper = ShopScraper()

        # Get Tesco products
        shop_ids = db.get_shop_ids()
        product_list = scraper.scrape(TESCO_CEREAL_URL, shop_ids.get("Tesco"))

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
