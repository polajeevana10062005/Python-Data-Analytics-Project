import math
import statistics
import re

import numpy as np
import pandas as pd


class DataProcessor:

    processor_count = 0

    def __init__(self, input_file="raw_products.csv"):
        self.input_file = input_file
        self.df = None

        DataProcessor.processor_count += 1

    # =========================================================
    # 1. LOAD DATA
    # =========================================================

    def load_data(self):

        print()
        print("=" * 60)
        print("LOADING RAW DATA")
        print("=" * 60)

        self.df = pd.read_csv(
            self.input_file
        )

        print(
            f"Rows loaded: {len(self.df)}"
        )

        print(
            f"Columns loaded: {len(self.df.columns)}"
        )

        return self.df

    # =========================================================
    # 2. CHECK REQUIRED COLUMNS
    # =========================================================

    def check_columns(self):

        required_columns = [
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

        missing_columns = [
            column
            for column in required_columns
            if column not in self.df.columns
        ]

        if missing_columns:

            raise ValueError(
                "Missing columns: "
                + ", ".join(missing_columns)
            )

        print()
        print("All required columns are present.")

    # =========================================================
    # 3. CONVERT NUMERIC COLUMNS
    # =========================================================

    def convert_numeric_columns(self):

        numeric_columns = [
            "Price",
            "Discount",
            "Rating",
            "Number of Reviews"
        ]

        for column in numeric_columns:

            self.df[column] = pd.to_numeric(
                self.df[column],
                errors="coerce"
            )

        print()
        print("Numeric columns converted successfully.")

    # =========================================================
    # 4. CLEAN PRODUCT IDs
    # =========================================================

    def clean_product_ids(self):

        self.df["Product ID"] = (
            self.df["Product ID"]
            .fillna("")
            .astype(str)
            .str.strip()
        )

        # Replace empty IDs
        empty_ids = (
            self.df["Product ID"] == ""
        )

        empty_count = empty_ids.sum()

        if empty_count > 0:

            for index in self.df.index[empty_ids]:

                self.df.at[
                    index,
                    "Product ID"
                ] = (
                    f"PRODUCT-{index + 1:04d}"
                )

        # Make IDs unique if duplicates exist
        seen_ids = set()

        for index in self.df.index:

            product_id = self.df.at[
                index,
                "Product ID"
            ]

            original_id = product_id
            counter = 1

            while product_id in seen_ids:

                product_id = (
                    f"{original_id}-{counter}"
                )

                counter += 1

            self.df.at[
                index,
                "Product ID"
            ] = product_id

            seen_ids.add(product_id)

        print(
            "Product IDs cleaned and made unique."
        )

    # =========================================================
    # 5. CLEAN TEXT FIELDS
    # =========================================================

    @staticmethod
    def clean_text(value):

        if pd.isna(value):
            return ""

        value = str(value)

        value = re.sub(
            r"\s+",
            " ",
            value
        )

        value = value.strip()

        return value

    def clean_text_columns(self):

        text_columns = [
            "Product Name",
            "Category",
            "Availability",
            "Product URL"
        ]

        for column in text_columns:

            self.df[column] = (
                self.df[column]
                .apply(self.clean_text)
            )

        print(
            "Text fields cleaned successfully."
        )

    # =========================================================
    # 6. HANDLE MISSING VALUES
    # =========================================================

    def handle_missing_values(self):

        # Product Name
        self.df["Product Name"] = (
            self.df["Product Name"]
            .replace("", np.nan)
            .fillna("Unknown Product")
        )

        # Category
        self.df["Category"] = (
            self.df["Category"]
            .replace("", np.nan)
            .fillna("Unknown")
        )

        # Availability
        self.df["Availability"] = (
            self.df["Availability"]
            .replace("", np.nan)
            .fillna("Unknown")
        )

        # URL
        self.df["Product URL"] = (
            self.df["Product URL"]
            .replace("", np.nan)
            .fillna("Not Available")
        )

        # Numeric columns
        self.df["Price"] = (
            self.df["Price"]
            .fillna(0)
        )

        self.df["Discount"] = (
            self.df["Discount"]
            .fillna(0)
        )

        self.df["Rating"] = (
            self.df["Rating"]
            .fillna(0)
        )

        self.df["Number of Reviews"] = (
            self.df["Number of Reviews"]
            .fillna(0)
        )

        print(
            "Missing values handled successfully."
        )

    # =========================================================
    # 7. REMOVE DUPLICATES
    # =========================================================

    def remove_duplicates(self):

        before_count = len(
            self.df
        )

        self.df = (
            self.df
            .drop_duplicates(
                subset=["Product ID"]
            )
            .reset_index(drop=True)
        )

        after_count = len(
            self.df
        )

        removed = (
            before_count - after_count
        )

        print(
            f"Duplicate products removed: "
            f"{removed}"
        )

    # =========================================================
    # 8. STRING OPERATIONS
    # =========================================================

    def create_cleaned_names(self):

        # Lowercase
        self.df["Product Name Lower"] = (
            self.df["Product Name"]
            .str.lower()
        )

        # Uppercase
        self.df["Product Name Upper"] = (
            self.df["Product Name"]
            .str.upper()
        )

        # Product name length
        self.df["Product Name Length"] = (
            self.df["Product Name"]
            .str.len()
        )

        # Word count
        self.df["Product Name Word Count"] = (
            self.df["Product Name"]
            .str.split()
            .str.len()
        )

        # Cleaned product names list
        cleaned_product_names = [
            self.clean_text(name)
            for name in self.df["Product Name"]
        ]

        self.cleaned_product_names = (
            cleaned_product_names
        )

        print()
        print(
            "String operations completed."
        )

        print(
            "List comprehension created:"
        )

        print(
            self.cleaned_product_names[:5]
        )

    # =========================================================
    # 9. FINAL PRICE
    # =========================================================

    def calculate_final_price(self):

        self.df["final_price"] = (
            self.df["Price"]
            * (
                1
                - self.df["Discount"] / 100
            )
        )

        self.df["final_price"] = (
            self.df["final_price"]
            .round(2)
        )

        print()
        print(
            "final_price column created."
        )

    # =========================================================
    # 10. REVENUE
    # =========================================================

    def calculate_revenue(self):

        self.df[
            "total_estimated_revenue"
        ] = (
            self.df["final_price"]
            * self.df["Number of Reviews"]
        )

        self.df[
            "total_estimated_revenue"
        ] = (
            self.df[
                "total_estimated_revenue"
            ]
            .round(2)
        )

        print(
            "total_estimated_revenue "
            "column created."
        )

    # =========================================================
    # 11. AVERAGE SCORE
    # =========================================================

    def calculate_average_score(self):

        self.df["average_score"] = (
            self.df["Rating"]
            * (
                1
                + np.log1p(
                    self.df["Number of Reviews"]
                )
            )
        )

        self.df["average_score"] = (
            self.df["average_score"]
            .round(2)
        )

        print(
            "average_score column created."
        )

    # =========================================================
    # 12. PRICE BANDS
    # =========================================================

    @staticmethod
    def price_band(price):

        if price < 20:
            return "Low"

        elif price <= 50:
            return "Medium"

        else:
            return "High"

    def classify_price_bands(self):

        self.df["Price Band"] = (
            self.df["Price"]
            .apply(self.price_band)
        )

        print()
        print(
            "Price bands created:"
        )

        print(
            self.df["Price Band"]
            .value_counts()
        )

    # =========================================================
    # 13. RATING CLASSIFICATION
    # =========================================================

    @staticmethod
    def rating_category(rating):

        if rating >= 4:
            return "Excellent"

        elif rating >= 3:
            return "Good"

        elif rating >= 2:
            return "Average"

        else:
            return "Low"

    def classify_ratings(self):

        self.df["Rating Category"] = (
            self.df["Rating"]
            .apply(
                self.rating_category
            )
        )

        print()
        print(
            "Rating categories created:"
        )

        print(
            self.df["Rating Category"]
            .value_counts()
        )

    # =========================================================
    # 14. HOT PICKS
    # =========================================================

    def identify_hot_picks(self):

        self.df["Hot Pick"] = (
            (
                self.df["Rating"] >= 4
            )
            &
            (
                self.df["Number of Reviews"] >= 0
            )
        )

        hot_pick_count = int(
            self.df["Hot Pick"].sum()
        )

        print()
        print(
            f"Hot picks identified: "
            f"{hot_pick_count}"
        )

    # =========================================================
    # 15. PRODUCT TUPLES
    # =========================================================

    def create_product_tuples(self):

        self.product_tuples = [
            (
                row["Product ID"],
                row["Product Name"],
                row["Category"],
                row["Price"]
            )
            for _, row in self.df.iterrows()
        ]

        print()
        print(
            "Product tuples created."
        )

        print(
            self.product_tuples[:3]
        )

    # =========================================================
    # 16. PRODUCT DICTIONARY
    # =========================================================

    def create_product_dictionary(self):

        self.product_dictionary = {
            row["Product ID"]: (
                row["Product Name"],
                row["Category"],
                row["Price"],
                row["Rating"]
            )
            for _, row in self.df.iterrows()
        }

        print()
        print(
            "Product dictionary created."
        )

        print(
            f"Dictionary size: "
            f"{len(self.product_dictionary)}"
        )

    # =========================================================
    # 17. CATEGORY COUNT DICTIONARY
    # =========================================================

    def create_category_count_dictionary(self):

        category_counts = {}

        for category in self.df["Category"]:

            if category not in category_counts:

                category_counts[category] = 0

            category_counts[category] += 1

        self.category_count_dictionary = (
            category_counts
        )

        print()
        print(
            "Category count dictionary:"
        )

        print(
            self.category_count_dictionary
        )

    # =========================================================
    # 18. CATEGORY PRICE DICTIONARY
    # =========================================================

    def create_category_price_dictionary(self):

        category_prices = {}

        for _, row in self.df.iterrows():

            category = row["Category"]
            price = row["Price"]

            if category not in category_prices:

                category_prices[category] = []

            category_prices[category].append(
                price
            )

        self.category_price_dictionary = (
            category_prices
        )

        print()
        print(
            "Category price dictionary created."
        )

    # =========================================================
    # 19. MATH AND STATISTICS
    # =========================================================

    def calculate_statistics(self):

        prices = (
            self.df["Price"]
            .dropna()
            .tolist()
        )

        if prices:

            mean_price = statistics.mean(
                prices
            )

            median_price = statistics.median(
                prices
            )

            min_price = min(
                prices
            )

            max_price = max(
                prices
            )

            standard_deviation = (
                statistics.stdev(prices)
                if len(prices) > 1
                else 0
            )

            price_range = (
                max_price - min_price
            )

            geometric_example = math.sqrt(
                max_price
                if max_price > 0
                else 0
            )

            print()
            print("=" * 60)
            print("PRICE STATISTICS")
            print("=" * 60)

            print(
                f"Mean price: "
                f"{mean_price:.2f}"
            )

            print(
                f"Median price: "
                f"{median_price:.2f}"
            )

            print(
                f"Minimum price: "
                f"{min_price:.2f}"
            )

            print(
                f"Maximum price: "
                f"{max_price:.2f}"
            )

            print(
                f"Standard deviation: "
                f"{standard_deviation:.2f}"
            )

            print(
                f"Price range: "
                f"{price_range:.2f}"
            )

            print(
                f"Square root of maximum price: "
                f"{geometric_example:.2f}"
            )

    # =========================================================
    # 20. NUMPY OPERATIONS
    # =========================================================

    def numpy_analysis(self):

        prices = self.df[
            "Price"
        ].to_numpy()

        ratings = self.df[
            "Rating"
        ].to_numpy()

        if len(prices) > 0:

            print()
            print("=" * 60)
            print("NUMPY ANALYSIS")
            print("=" * 60)

            print(
                f"NumPy price mean: "
                f"{np.mean(prices):.2f}"
            )

            print(
                f"NumPy price median: "
                f"{np.median(prices):.2f}"
            )

            print(
                f"NumPy price standard deviation: "
                f"{np.std(prices):.2f}"
            )

            print(
                f"NumPy average rating: "
                f"{np.mean(ratings):.2f}"
            )

    # =========================================================
    # 21. CATEGORY GROUPING
    # =========================================================

    def category_analysis(self):

        category_summary = (
            self.df
            .groupby("Category")
            .agg(
                Product_Count=(
                    "Product ID",
                    "count"
                ),
                Average_Price=(
                    "Price",
                    "mean"
                ),
                Average_Rating=(
                    "Rating",
                    "mean"
                ),
                Total_Revenue=(
                    "total_estimated_revenue",
                    "sum"
                )
            )
            .reset_index()
        )

        category_summary[
            "Average_Price"
        ] = (
            category_summary[
                "Average_Price"
            ]
            .round(2)
        )

        category_summary[
            "Average_Rating"
        ] = (
            category_summary[
                "Average_Rating"
            ]
            .round(2)
        )

        category_summary[
            "Total_Revenue"
        ] = (
            category_summary[
                "Total_Revenue"
            ]
            .round(2)
        )

        self.category_summary = (
            category_summary
        )

        print()
        print("=" * 60)
        print("CATEGORY SUMMARY")
        print("=" * 60)

        print(
            self.category_summary
        )

    # =========================================================
    # 22. DATA QUALITY CHECK
    # =========================================================

    def data_quality_check(self):

        print()
        print("=" * 60)
        print("DATA QUALITY CHECK")
        print("=" * 60)

        print(
            f"Total rows: {len(self.df)}"
        )

        print(
            f"Duplicate Product IDs: "
            f"{self.df['Product ID'].duplicated().sum()}"
        )

        print(
            f"Missing Product Names: "
            f"{self.df['Product Name'].isna().sum()}"
        )

        print(
            f"Missing Prices: "
            f"{self.df['Price'].isna().sum()}"
        )

        print(
            f"Missing Ratings: "
            f"{self.df['Rating'].isna().sum()}"
        )

        print(
            f"Missing Categories: "
            f"{self.df['Category'].isna().sum()}"
        )

    # =========================================================
    # 23. SAVE PROCESSED DATA
    # =========================================================

    def save_processed_data(
        self,
        filename="clean_products.csv"
    ):

        self.df.to_csv(
            filename,
            index=False,
            encoding="utf-8"
        )

        print()
        print(
            f"Processed data saved to "
            f"{filename}"
        )

    # =========================================================
    # 24. RUN ALL PROCESSING
    # =========================================================

    def process(self):

        self.load_data()

        self.check_columns()

        self.convert_numeric_columns()

        self.clean_product_ids()

        self.clean_text_columns()

        self.handle_missing_values()

        self.remove_duplicates()

        self.create_cleaned_names()

        self.calculate_final_price()

        self.calculate_revenue()

        self.calculate_average_score()

        self.classify_price_bands()

        self.classify_ratings()

        self.identify_hot_picks()

        self.create_product_tuples()

        self.create_product_dictionary()

        self.create_category_count_dictionary()

        self.create_category_price_dictionary()

        self.calculate_statistics()

        self.numpy_analysis()

        self.category_analysis()

        self.data_quality_check()

        self.save_processed_data()

        return self.df


# =============================================================
# MAIN PROGRAM
# =============================================================

if __name__ == "__main__":

    processor = DataProcessor(
        input_file="raw_products.csv"
    )

    processed_data = processor.process()

    print()
    print("=" * 60)
    print("PROCESSING COMPLETED")
    print("=" * 60)

    print(
        f"Final processed rows: "
        f"{len(processed_data)}"
    )

    print()
    print(
        "Output file:"
    )

    print(
        "clean_products.csv"
    )