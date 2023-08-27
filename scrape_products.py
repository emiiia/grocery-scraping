from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import re
from urllib.parse import urlparse


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

        for i, li in enumerate(li_tags):
            # Get product titles
            title_link = li.find(
                lambda tag: tag.name == "a"
                and any(
                    "product-tile--title" in str(value)
                    for _, value in tag.attrs.items()
                )
            )

            # If required fields aren't found, skip product
            if not title_link or not title_link.text or not title_link.text.strip():
                continue

            # Set initial values
            price = None
            promotion_price = None
            promotion_text = None
            rating = 0
            featured = 0
            vegetarian = 0
            vegan = 0
            in_stock = 1

            # Get prices
            price_p = li.find("p", text=re.compile(r"^£\d+(\.\d{1,2})?$"))
            if price_p and price_p.text and price_p.text.strip():
                price = float(price_p.text.strip().replace("£", ""))

            # Get promotion (clubcard) prices
            promotion_price_span = li.find(
                "span", text=re.compile(r"^£\d+(\.\d{1,2})? Clubcard Price$")
            )
            if (
                promotion_price_span
                and promotion_price_span.text
                and promotion_price_span.text.strip()
            ):
                promotion_price = float(
                    promotion_price_span.text.strip()
                    .replace("£", "")
                    .replace("Clubcard Price", "")
                )

            # Get promotion
            promotion_span = li.find("span", class_="offer-text")
            if promotion_span and promotion_span.text and promotion_span.text.strip():
                promotion_text = promotion_span.text.strip()

            # Check whether product is out of stock
            # Price can be null if not in stock
            if li.find("p", text="This product's currently out of stock") or not price:
                in_stock = 0

            # Check whether product is featured
            if li.find("p", text="Sponsored"):
                featured = 1

            # Click on link to get detailed info
            href = title_link.get("href")
            if href:
                # Get base url and add href to scrape product page
                parsed_url = urlparse(url)
                base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
                product_page_url = base_url + href
                print("Scraping", product_page_url)
                self.driver.get(product_page_url)
                html = self.driver.page_source
                soup = BeautifulSoup(html, "html.parser")

                # Get rating
                rating_span = soup.find(
                    lambda tag: tag.name == "span"
                    and "rating" in " ".join(tag.get("class", []))
                    and re.search(r"^\d(\.\d{1,1})?$", tag.text)
                )
                if rating_span and rating_span.text and rating_span.text.strip:
                    rating = float(rating_span.text.strip())

            product_list.append(
                {
                    "name": title_link.text.strip(),
                    "price": price,
                    "promotion_price": promotion_price,
                    "promotion": promotion_text,
                    "rating": rating,
                    "featured": featured,
                    "vegetarian": vegetarian,
                    "vegan": vegan,
                    "in_stock": in_stock,
                    "brand": "Crunchy Nut",
                    "company": "Kellog's",
                    "shop_id": shop_id,
                }
            )

            # TODO Remove
            if i == 2:
                break

        return product_list

    def close(self):
        self.driver.quit()
