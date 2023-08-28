from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
import re
from urllib.parse import urlparse
from product import Product
from selenium.webdriver.common.by import By

PRICE_REGEX = r"^£\d+(\.\d{1,2})?$"
RATING_REGEX = r"^\d(\.\d{1,1})?$"


class ShopScraper(object):
    def __init__(self):
        options = ChromeOptions()
        options.add_argument("--headless=new")
        options.add_argument("--enable-javascript")
        self.driver = webdriver.Chrome(options=options)
        self.MAX_BRANDS = None
        self.MAX_PRODUCTS = None

    def scrape_tesco_brands(self, shop_id):
        product_list = []
        url = "https://www.tesco.com/groceries/en-GB/shop/food-cupboard/cereals/all"
        self.driver.get(url)
        self.driver.implicitly_wait(10)

        # Open brands tab
        button = self.driver.find_element(
            By.XPATH, '//button[@aria-controls="filter-brands"]'
        )
        self.driver.implicitly_wait(10)
        button.click()
        html = self.driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        brands_div = soup.find("div", id="filter-brands")

        # Find links within brands tab
        brand_links = []
        if brands_div:
            brand_links = brands_div.find_all("a", class_="filter-option--link")
            for i, link in enumerate(brand_links):
                try:
                    brand_tag = link.find("span", class_="filter-label--line--inline")
                    href = link.get("href")
                    brand_url = self.get_url_with_href(url, href)
                    product_list += self.scrape_tesco(shop_id, brand_url, brand_tag)
                    if self.MAX_BRANDS and i == self.MAX_BRANDS - 1:
                        break
                except Exception as err:
                    print("Error scraping Tesco:", brand_url, err)
                    continue

        return product_list

    def scrape_ocado_brands(self, shop_id):
        product_list = []
        url = "https://www.ocado.com/browse/food-cupboard-20424/breakfast-cereals-38715"
        soup = self.get_soup(url)

        # Find the ul containing brand links
        ul = None
        div = soup.find(
            lambda tag: tag.name == "div"
            and "filter-list" in " ".join(tag.get("class", []))
        )
        if div:
            h3 = div.find("h3", text="Brands")
            if h3:
                ul = h3.find_next("ul")

        # Find links within brands tab
        brand_links = []
        if ul:
            brand_links = ul.find_all("a")
            for i, link in enumerate(brand_links):
                try:
                    href = link.get("href")
                    brand_url = self.get_url_with_href(url, href)
                    product_list += self.scrape_ocado(
                        shop_id, self.get_url_with_href(url, href), link
                    )
                    if self.MAX_BRANDS and i == self.MAX_BRANDS - 1:
                        break
                except Exception as err:
                    print("Error scraping Ocado:", brand_url, err)
                    continue

        return product_list

    def scrape_tesco(self, shop_id, url, brand_tag):
        print("Scraping", url)
        soup = self.get_soup(url)

        product_list = []
        li_tags = self.get_list_items(soup, "product-list--list-item")
        for i, li in enumerate(li_tags):
            product = Product(shop_id)

            # Set product title
            product.set_title(li, "a", "product-tile--title")
            # Set brand name
            product.set_brand(brand_tag)

            # If required fields aren't found, skip product
            if not product.get_title() or not product.get_brand():
                continue

            # Get prices
            product.set_price(li.find("p", text=re.compile(PRICE_REGEX)))

            # Get promotion (clubcard) prices
            product.set_promotion_price(
                li.find("span", text=re.compile(r"^£\d+(\.\d{1,2})? Clubcard Price$")),
                "Clubcard Price",
            )

            # Get promotion
            product.set_promotion(li.find("span", class_="offer-text"))

            # Check whether item is in stock
            product.set_in_stock(li)

            # Check whether product is featured
            if li.find("p", string="Sponsored"):
                product.set_featured(1)

            # Click on link to get detailed info
            product_soup = self.scrape_product_page(url, product.get_product_link(li))
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

            if self.MAX_PRODUCTS and i == self.MAX_PRODUCTS - 1:
                break

        return product_list

    def scrape_ocado(self, shop_id, url, brand_tag):
        print("Scraping", url)
        soup = self.get_soup(url)

        product_list = []
        li_tags = self.get_list_items(soup, "fops-item fops-item--")
        for i, li in enumerate(li_tags):
            product = Product(shop_id)

            # Set product title
            product.set_title(li, "h4", "fop-title")
            # If required fields aren't found, skip product
            if not product.get_title():
                continue

            # Set brand name
            product.set_brand(brand_tag)

            # Get prices - first find old price if there is a promotion
            price_span = li.find(
                lambda tag: tag.name == "span"
                and "fop-old-price" in " ".join(tag.get("class", []))
                and re.search(PRICE_REGEX, tag.text)
            )
            if not price_span:
                # If no promotion - set price
                price_span = li.find("span", class_="fop-price")
            else:
                # Get promotion price
                promotion_price_span = li.find(
                    lambda tag: tag.name == "span"
                    and "fop-price price-offer" in " ".join(tag.get("class", []))
                    and re.search(PRICE_REGEX, tag.text)
                )
                product.set_promotion_price(promotion_price_span)
            product.set_price(price_span)

            # Get promotion
            product.set_promotion(
                li.find(
                    lambda tag: tag.name == "a"
                    and "promotion-offer" in " ".join(tag.get("class", []))
                )
            )

            # Check whether item is in stock
            product.set_in_stock(li)

            # Check whether product is featured
            if li.find(
                lambda tag: tag.name == "div"
                and "featured" in " ".join(tag.get("class", []))
            ):
                product.featured = 1

            # Click on link to get detailed info
            product_soup = self.scrape_product_page(url, product.get_product_link(li))
            if product_soup:
                # Get rating
                rating_span = product_soup.find(
                    lambda tag: tag.name == "span"
                    and "reviewSummary" in " ".join(tag.get("class", []))
                    and any("rating" in str(value) for _, value in tag.attrs.items())
                )
                product.set_rating(rating_span)

                product.set_vegan_vegetarian(product_soup)

            product_list.append(product.get_product())

            if self.MAX_PRODUCTS and i == self.MAX_PRODUCTS - 1:
                break

        return product_list

    def scrape_product_page(self, url, anchor_tag):
        # Click on link to get detailed info
        href = anchor_tag.get("href")
        if href:
            product_page_url = self.get_url_with_href(url, href)
            print("Scraping", product_page_url)
            return self.get_soup(product_page_url)

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

    def get_url_with_href(self, url, href):
        # Get base url and add href
        parsed_url = urlparse(url)
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
        return base_url + href

    def close(self):
        self.driver.quit()
