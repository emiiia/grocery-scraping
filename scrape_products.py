from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options


class ShopScraper(object):
    def __init__(self):
        options = Options()
        options.add_argument("--headless=new")
        options.add_argument("--enable-javascript")
        self.driver = webdriver.Firefox(options=options)

    def scrape(self, url, shop_id):
        print('Getting', url)
        self.driver.get(url)
        html = self.driver.page_source
        soup = BeautifulSoup(html, "html.parser")

        print(soup)

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
                "in_stock": 0,
            }
        ]

        return product_list

    def close(self):
        self.driver.quit()