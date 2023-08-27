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
        product_list = []
        print("Scraping", url)
        self.driver.get(url)
        html = self.driver.page_source
        soup = BeautifulSoup(html, "html.parser")

        # Get product list items
        li_tags = soup.find_all(
            lambda tag: tag.name == "li"
            and "product-list--list-item" in " ".join(tag.get("class", []))
        )

        for li in li_tags:
            # Get product titles
            title_link = li.find(
                lambda tag: tag.name == "a"
                and any(
                    "product-tile--title" in str(value)
                    for _, value in tag.attrs.items()
                )
            )

            if not title_link or not title_link.text or not title_link.text.strip():
                continue

            product_list.append(
                {
                    "name": title_link.text.strip(),
                    "price": 4,
                    "discounted_price": 3,
                    "rating": 2,
                    "featured": 0,
                    "vegetarian": 0,
                    "vegan": 0,
                    "in_stock": 0,
                    "brand": "Crunchy Nut",
                    "company": "Kellog's",
                    "shop_id": shop_id,
                }
            )

        return product_list

    def close(self):
        self.driver.quit()
