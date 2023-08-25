from manage_db import GroceriesDB
from scrape_products import ShopScraper

TESCO_CEREAL_URL = (
    "https://www.tesco.com/groceries/en-GB/shop/food-cupboard/cereals/all"
)
OCADO_CEREAL_URL = (
    "https://www.ocado.com/browse/food-cupboard-20424/breakfast-cereals-38715"
)


def main():
    # Initialise web driver
    scraper = ShopScraper()

    # Initialise database
    db = GroceriesDB()

    # Get Tesco products
    shop_ids = db.get_shop_ids()
    product_list = scraper.scrape(TESCO_CEREAL_URL, shop_ids.get("Tesco"))

    # Insert to Product table and close db
    db.insert_data(product_list)
    db.close()
    scraper.close()


if __name__ == "__main__":
    main()

