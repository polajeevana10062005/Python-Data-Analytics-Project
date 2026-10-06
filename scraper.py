import csv
import re
import time
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


class Scraper:

    scraper_count = 0

    def __init__(
        self,
        base_url,
        target_products=100,
        max_pages=10
    ):
        self.base_url = base_url
        self.target_products = target_products
        self.max_pages = max_pages

        self.products = []

        self.session = requests.Session()

        self.session.headers.update({
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 "
                "(KHTML, like Gecko) "
                "Chrome/151.0.0.0 Safari/537.36"
            ),
            "Accept": (
                "text/html,application/xhtml+xml,"
                "application/xml;q=0.9,image/avif,image/webp,"
                "image/apng,*/*;q=0.8"
            ),
            "Accept-Language": "en-US,en;q=0.9"
        })

        Scraper.scraper_count += 1

    # =========================================================
    # FETCH DATA
    # =========================================================

    def fetch_data(self, url):

        try:

            print()
            print(f"Fetching URL: {url}")

            response = self.session.get(
                url,
                timeout=30
            )

            print(
                f"HTTP Status Code: "
                f"{response.status_code}"
            )

            response.raise_for_status()

            print("Page fetched successfully.")

            return response.text

        except requests.exceptions.RequestException as error:

            print(
                f"Error while fetching page: {error}"
            )

            return None

    # =========================================================
    # CLEAN TEXT
    # =========================================================

    @staticmethod
    def clean_text(element):

        if element is None:
            return ""

        return " ".join(
            element.get_text(
                " ",
                strip=True
            ).split()
        )

    # =========================================================
    # EXTRACT PRICE
    # =========================================================

    @staticmethod
    def extract_price(text):

        if not text:
            return None

        match = re.search(
            r"£\s*([\d,]+(?:\.\d+)?)",
            text
        )

        if match:

            try:

                return float(
                    match.group(1).replace(
                        ",",
                        ""
                    )
                )

            except ValueError:

                return None

        return None

    # =========================================================
    # EXTRACT RATING
    # =========================================================

    @staticmethod
    def extract_rating(element):

        if element is None:
            return None

        rating_class = element.get(
            "class",
            []
        )

        rating_map = {
            "One": 1,
            "Two": 2,
            "Three": 3,
            "Four": 4,
            "Five": 5
        }

        for rating_name in rating_map:

            if rating_name in rating_class:

                return rating_map[
                    rating_name
                ]

        return None

    # =========================================================
    # PRODUCT ID
    # =========================================================

    @staticmethod
    def extract_product_id(
        product_url
    ):

        if not product_url:
            return ""

        match = re.search(
            r"/catalogue/([^/]+)/",
            product_url
        )

        if match:

            product_name = match.group(1)

            product_name = re.sub(
                r"[^A-Za-z0-9]+",
                "-",
                product_name
            )

            return product_name.upper()

        return ""

    # =========================================================
    # DISCOUNT
    # =========================================================

    @staticmethod
    def calculate_discount(price):

        if price is None:
            return 0.0

        # Books to Scrape does not provide
        # an original/list price.
        #
        # Therefore we keep the real
        # scraped discount as 0.
        return 0.0

    # =========================================================
    # PARSE PRODUCT CARD
    # =========================================================

    def parse_product_card(
        self,
        card,
        index
    ):

        # -----------------------------------------------------
        # PRODUCT NAME
        # -----------------------------------------------------

        name_element = card.select_one(
            "h3 a"
        )

        product_name = ""

        if name_element:

            product_name = (
                name_element.get(
                    "title",
                    ""
                ).strip()
            )

            if not product_name:

                product_name = self.clean_text(
                    name_element
                )

        # -----------------------------------------------------
        # PRODUCT URL
        # -----------------------------------------------------

        product_url = ""

        if name_element:

            href = name_element.get(
                "href",
                ""
            )

            product_url = urljoin(
                self.base_url,
                href
            )

        # -----------------------------------------------------
        # PRODUCT ID
        # -----------------------------------------------------

        product_id = (
            self.extract_product_id(
                product_url
            )
        )

        if not product_id:

            product_id = (
                f"BOOK-{index:04d}"
            )

        # -----------------------------------------------------
        # CATEGORY
        # -----------------------------------------------------

        category = "Books"

        # -----------------------------------------------------
        # PRICE
        # -----------------------------------------------------

        price_element = card.select_one(
            ".price_color"
        )

        price = None

        if price_element:

            price = self.extract_price(
                self.clean_text(
                    price_element
                )
            )

        # -----------------------------------------------------
        # RATING
        # -----------------------------------------------------

        rating_element = card.select_one(
            "p.star-rating"
        )

        rating = self.extract_rating(
            rating_element
        )

        # -----------------------------------------------------
        # DISCOUNT
        # -----------------------------------------------------

        discount = self.calculate_discount(
            price
        )

        # -----------------------------------------------------
        # REVIEWS
        # -----------------------------------------------------

        # Books to Scrape does not expose
        # review counts on the listing page.
        #
        # Keep the value as 0 rather than
        # inventing a number.

        reviews = 0

        # -----------------------------------------------------
        # AVAILABILITY
        # -----------------------------------------------------

        availability_element = card.select_one(
            ".availability"
        )

        availability = (
            self.clean_text(
                availability_element
            )
        )

        if not availability:

            availability = "Unknown"

        # -----------------------------------------------------
        # IGNORE EMPTY CARD
        # -----------------------------------------------------

        if not product_name:

            return None

        # -----------------------------------------------------
        # RETURN PRODUCT
        # -----------------------------------------------------

        return {
            "Product ID": str(product_id),
            "Product Name": product_name,
            "Category": category,
            "Price": price,
            "Discount": discount,
            "Rating": rating,
            "Number of Reviews": reviews,
            "Availability": availability,
            "Product URL": product_url
        }

    # =========================================================
    # PARSE HTML
    # =========================================================

    def parse_html(
        self,
        html
    ):

        soup = BeautifulSoup(
            html,
            "html.parser"
        )

        cards = soup.select(
            "article.product_pod"
        )

        print(
            f"Product cards detected: "
            f"{len(cards)}"
        )

        parsed_products = []

        start_index = (
            len(self.products) + 1
        )

        for index, card in enumerate(
            cards,
            start=start_index
        ):

            product = (
                self.parse_product_card(
                    card,
                    index
                )
            )

            if product:

                parsed_products.append(
                    product
                )

        return parsed_products

    # =========================================================
    # GET NEXT PAGE
    # =========================================================

    def get_next_page_url(
        self,
        html,
        current_url
    ):

        soup = BeautifulSoup(
            html,
            "html.parser"
        )

        next_link = soup.select_one(
            "li.next a"
        )

        if next_link:

            href = next_link.get(
                "href",
                ""
            )

            if href:

                return urljoin(
                    current_url,
                    href
                )

        return None

    # =========================================================
    # SCRAPE
    # =========================================================

    def scrape(self):

        current_url = self.base_url

        visited_urls = set()

        page_number = 1

        while (
            len(self.products)
            < self.target_products
            and page_number <= self.max_pages
        ):

            print()
            print("=" * 60)

            print(
                f"Scraping page {page_number}"
            )

            print("=" * 60)

            # Prevent duplicate pages
            if current_url in visited_urls:

                print(
                    "This page was already visited."
                )

                break

            visited_urls.add(
                current_url
            )

            # -------------------------------------------------
            # FETCH
            # -------------------------------------------------

            html = self.fetch_data(
                current_url
            )

            if html is None:

                print(
                    "Could not fetch page."
                )

                break

            # -------------------------------------------------
            # PARSE
            # -------------------------------------------------

            page_products = (
                self.parse_html(
                    html
                )
            )

            print(
                f"Products extracted from "
                f"this page: "
                f"{len(page_products)}"
            )

            if not page_products:

                print(
                    "No products found."
                )

                break

            # -------------------------------------------------
            # REMOVE DUPLICATES
            # -------------------------------------------------

            existing_ids = {
                product["Product ID"]
                for product in self.products
            }

            new_products = 0

            for product in page_products:

                product_id = product[
                    "Product ID"
                ]

                if product_id not in existing_ids:

                    self.products.append(
                        product
                    )

                    existing_ids.add(
                        product_id
                    )

                    new_products += 1

                if (
                    len(self.products)
                    >= self.target_products
                ):

                    break

            print(
                f"New unique products added: "
                f"{new_products}"
            )

            print(
                f"Total products collected: "
                f"{len(self.products)}"
            )

            # -------------------------------------------------
            # TARGET REACHED
            # -------------------------------------------------

            if (
                len(self.products)
                >= self.target_products
            ):

                print(
                    "Target product count reached."
                )

                break

            # -------------------------------------------------
            # NEXT PAGE
            # -------------------------------------------------

            next_url = (
                self.get_next_page_url(
                    html,
                    current_url
                )
            )

            if not next_url:

                print(
                    "No next page found."
                )

                break

            print(
                f"Next page URL: "
                f"{next_url}"
            )

            current_url = next_url

            page_number += 1

            time.sleep(1)

        return self.products

    # =========================================================
    # SAVE CSV
    # =========================================================

    def save_to_csv(
        self,
        filename="raw_products.csv"
    ):

        if not self.products:

            print(
                "No products available "
                "to save."
            )

            return

        fieldnames = [
            "Product ID",
            "Product Name",
            "Category",
            "Price",
            "Discount",
            "Rating",
            "Number of Reviews",
            "Availability",
            "Product URL"
        ]

        with open(
            filename,
            "w",
            newline="",
            encoding="utf-8"
        ) as file:

            writer = csv.DictWriter(
                file,
                fieldnames=fieldnames
            )

            writer.writeheader()

            writer.writerows(
                self.products
            )

        print()
        print(
            f"Data saved successfully to "
            f"{filename}"
        )


# =============================================================
# MAIN PROGRAM
# =============================================================

if __name__ == "__main__":

    URL = "https://books.toscrape.com/"

    scraper = Scraper(
        base_url=URL,
        target_products=100,
        max_pages=10
    )

    products = scraper.scrape()

    print()
    print("=" * 60)

    print(
        f"FINAL PRODUCT COUNT: "
        f"{len(products)}"
    )

    print("=" * 60)

    scraper.save_to_csv(
        "raw_products.csv"
    )