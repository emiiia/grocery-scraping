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
            title = self.get_tag_text(title_link)
            if not title:
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
            price_text = self.get_tag_text(price_p)
            if price_text:
                # Format to get decimal price
                price = float(price_text.replace("£", ""))

            # Get promotion (clubcard) prices
            promotion_price_span = li.find(
                "span", text=re.compile(r"^£\d+(\.\d{1,2})? Clubcard Price$")
            )
            promotion_price_text = self.get_tag_text(promotion_price_span)
            if promotion_price_text:
                # Format to get decimal price
                promotion_price = float(
                    promotion_price_text.replace("£", "").replace("Clubcard Price", "")
                )

            # Get promotion
            promotion_span = li.find("span", class_="offer-text")
            promotion_text = self.get_tag_text(promotion_span)

            # Check whether product is out of stock
            # Price can be null if not in stock
            if (
                li.find("p", string="This product's currently out of stock")
                or not price
            ):
                in_stock = 0

            # Check whether product is featured
            if li.find("p", string="Sponsored"):
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
                rating_text = self.get_tag_text(rating_span)
                if rating_text:
                    # Format to get decimal rating
                    rating = float(rating_text)

                # Check whether vegetarian or vegan
                vegetarian_tag = soup.find(
                    None, text=re.compile("Suitable for Vegetarians", re.IGNORECASE)
                )
                vegan_tag = soup.find(
                    None, text=re.compile("Suitable for Vegans", re.IGNORECASE)
                )
                if vegetarian_tag:
                    vegetarian = 1
                if vegan_tag:
                    vegetarian = 1
                    vegan = 1

            product_list.append(
                {
                    "name": title,
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

    def get_tag_text(self, tag):
        """Helper function to check for null tag text"""
        if tag:
            return tag.get_text(separator=" ", strip=True)

    def close(self):
        self.driver.quit()
