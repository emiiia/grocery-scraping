from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import re


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

            # Get prices
            price_p = li.find(
                lambda tag: tag.name == "p"
                and "price__text" in " ".join(tag.get("class", []))
            )
            if price_p and price_p.text and price_p.text.strip():
                price = float(price_p.text.strip().replace("£", ""))

            # Get promotion prices
            promotion_price = None
            promotion_price_span = li.find("span", class_="offer-text")
            if (
                promotion_price_span
                and promotion_price_span.text
                and promotion_price_span.text.strip()
            ):
                promotion_text = promotion_price_span.text.strip()
                if re.search("^£\d+(\.\d{1,2})? Clubcard Price$", promotion_text):
                    promotion_text = promotion_text.replace("£", "")
                    promotion_text = promotion_text.replace("Clubcard Price", "")
                    promotion_price = float(promotion_text)

            if (
                not title_link
                or not title_link.text
                or not title_link.text.strip()
                or not price
            ):
                continue

            product_list.append(
                {
                    "name": title_link.text.strip(),
                    "price": price,
                    "promotion_price": promotion_price,
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
