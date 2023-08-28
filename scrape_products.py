from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
import re
from urllib.parse import urlparse
from product import Product

PRICE_REGEX = r"^£\d+(\.\d{1,2})?$"
RATING_REGEX = r"^\d(\.\d{1,1})?$"


class ShopScraper(object):
    def __init__(self):
        options = ChromeOptions()
        options.add_argument("--headless=new")
        options.add_argument("--enable-javascript")
        self.driver = webdriver.Chrome(options=options)
        # Predetermined DOM information
        self.website_tags = {
            "Tesco": {
                "url": "https://www.tesco.com/groceries/en-GB/shop/food-cupboard/cereals/all",
                "list_class": "product-list--list-item",
                "title_tag": {"tag": "a", "class": "product-tile--title"},
            },
            "Ocado": {
                "url": "https://www.ocado.com/browse/food-cupboard-20424/breakfast-cereals-38715",
                "list_class": "fops-item fops-item--",
                "title_tag": {"tag": "h4", "class": "fop-title"},
            },
        }

    def get_soup(self, url):
        self.driver.get(url)
        html = self.driver.page_source
        return BeautifulSoup(html, "html.parser")

    def get_list_items(self, soup, list_class):
        # Get product list items
        return soup.find_all(
            lambda tag: tag.name == "li"
            and list_class in " ".join(tag.get("class", []))
        )

    def scrape_tescos(self, shop_id):
        url = "https://www.tesco.com/groceries/en-GB/shop/food-cupboard/cereals/all"
        print("Scraping", url)
        soup = self.get_soup(url)

        product_list = []
        li_tags = self.get_list_items(soup, "product-list--list-item")
        for i, li in enumerate(li_tags):
            product = Product(shop_id)

            # Set product title
            product.set_title(li, "a", "product-tile--title")
            # If required fields aren't found, skip product
            if not product.get_title():
                continue

            # Get prices
            price_p = li.find("p", text=re.compile(PRICE_REGEX))
            product.set_price(price_p)

            # Get promotion (clubcard) prices
            promotion_price_span = li.find(
                "span", text=re.compile(r"^£\d+(\.\d{1,2})? Clubcard Price$")
            )
            promotion_price_text = Product.get_tag_text(promotion_price_span)
            if promotion_price_text:
                # Format to get decimal price
                product.set_promotion_price(
                    float(
                        promotion_price_text.replace("£", "").replace(
                            "Clubcard Price", ""
                        )
                    )
                )

            # Get promotion
            promotion_span = li.find("span", class_="offer-text")
            product.set_promotion(promotion_span)

            # Check whether item is in stock
            product.set_in_stock(li)

            # Check whether product is featured
            if li.find("p", string="Sponsored"):
                product.set_featured(1)

            # Click on link to get detailed info
            product_soup = self.scrape_product_page(url, product.get_title_link())
            if product_soup:
                # Get rating
                rating_span = product_soup.find(
                    lambda tag: tag.name == "span"
                    and "rating" in " ".join(tag.get("class", []))
                    and re.search(RATING_REGEX, tag.text)
                )
                product.set_rating(rating_span)
                product.set_vegan_vegetarian(product_soup)

            product_list.append(product.get_product())

            # TODO Remove
            if i == 2:
                break

        return product_list

    def scrape_product_page(self, url, anchor_tag):
        # Click on link to get detailed info
        href = anchor_tag.get("href")
        if href:
            # Get base url and add href to scrape product page
            parsed_url = urlparse(url)
            base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
            product_page_url = base_url + href
            print("Scraping", product_page_url)
            return self.get_soup(product_page_url)

    def close(self):
        self.driver.quit()
