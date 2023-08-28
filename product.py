import re


class Product(object):
    def __init__(self, shop_id: int):
        # Set initial values
        self.title = None
        self.title_link = None
        self.price = None
        self.promotion_price = None
        self.promotion_text = None
        self.rating = 0
        self.featured = 0
        self.vegetarian = 0
        self.vegan = 0
        self.in_stock = 1
        self.brand = "Crunchy Nut"
        self.company = "Kellog's"
        self.shop_id = shop_id

    def set_title(self, li, tag_name: str, title_class: str):
        # Get product list items
        self.title_link = li.find(
            lambda tag: tag.name == tag_name
            and any(title_class in str(value) for _, value in tag.attrs.items())
        )
        self.title = Product.get_tag_text(self.title_link)

    def get_title(self):
        return self.title

    def get_title_link(self):
        return self.title_link

    def get_product(self):
        return {
            "name": self.title,
            "price": self.price,
            "promotion_price": self.promotion_price,
            "promotion": self.promotion_text,
            "rating": self.rating,
            "featured": self.featured,
            "vegetarian": self.vegetarian,
            "vegan": self.vegan,
            "in_stock": self.in_stock,
            "brand": self.brand,
            "company": self.company,
            "shop_id": self.shop_id,
        }

    def set_price(self, price_tag):
        price_text = Product.get_tag_text(price_tag)
        if price_text:
            # Format to get decimal price
            self.price = float(price_text.replace("£", ""))

    def set_promotion_price(self, price: float):
        self.promotion_price = price

    def set_promotion(self, promotion_tag):
        self.promotion = Product.get_tag_text(promotion_tag)

    def set_rating(self, rating_tag):
        rating_text = Product.get_tag_text(rating_tag)
        if rating_text:
            # Format to get decimal rating
            self.rating = float(rating_text)

    def set_featured(self, featured: int):
        self.featured = featured

    def set_vegan_vegetarian(self, soup):
        # Check whether vegetarian or vegan
        vegetarian_tag = soup.find(
            None, text=re.compile("Suitable for Vegetarians", re.IGNORECASE)
        )
        vegan_tag = soup.find(
            None, text=re.compile("Suitable for Vegans", re.IGNORECASE)
        )

        if vegetarian_tag:
            self.vegetarian = 1
        if vegan_tag:
            self.vegetarian = 1
            self.vegan = 1

    def set_in_stock(self, tag):
        # Check whether product is out of stock
        # Price can be null if not in stock
        if (
            tag.find("p", string="This product's currently out of stock")
            or not self.price
        ):
            self.in_stock = 0

    def set_brand(self, brand: str):
        self.brand = brand

    def set_company(self, company: str):
        self.company = company

    @staticmethod
    def get_tag_text(tag):
        """Helper function to check for null tag text"""
        if tag:
            return tag.get_text(separator=" ", strip=True)
