from manage_db import GroceriesDB
import requests
from bs4 import BeautifulSoup

TESCO_CEREAL_URL = (
    "https://www.tesco.com/groceries/en-GB/shop/food-cupboard/cereals/all"
)
OCADO_CEREAL_URL = (
    "https://www.ocado.com/browse/food-cupboard-20424/breakfast-cereals-38715"
)


def scrape_data(url, shop_id):
    # response = requests.get(url)
    # soup = BeautifulSoup(response.content, "html.parser")
    # print(soup)

    product_list = [
        {
            "shop_id": shop_id,
            "name": "Kellogg's Crunchy Nut Breakfast Cereal 500g",
            "price": 4,
            "discounted_price": 3,
            "rating": 2,
            "featured": 0,
            "vegetarian": 0,
            "vegan": 0,
        }
    ]

    return product_list


def main():
    db = GroceriesDB()
    shop_ids = db.get_shop_ids()
    product_list = scrape_data(TESCO_CEREAL_URL, shop_ids.get("Tesco"))
    db.insert_data(product_list)
    db.close()


if __name__ == "__main__":
    main()
