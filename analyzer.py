import os
import math
import statistics

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px


class AnalyzerVisualizer:

    analyzer_count = 0

    def __init__(
        self,
        input_file="clean_products.csv",
        charts_folder="charts",
        report_file="analysis_summary.txt"
    ):
        self.input_file = input_file
        self.charts_folder = charts_folder
        self.report_file = report_file
        self.df = None

        AnalyzerVisualizer.analyzer_count += 1

        # Create charts folder if it does not exist
        os.makedirs(
            self.charts_folder,
            exist_ok=True
        )

    # =========================================================
    # LOAD DATA
    # =========================================================

    def load_data(self):

        print()
        print("=" * 60)
        print("LOADING CLEAN PRODUCTS")
        print("=" * 60)

        try:

            self.df = pd.read_csv(
                self.input_file
            )

            print(
                f"Rows loaded: {len(self.df)}"
            )

            print(
                f"Columns loaded: {len(self.df.columns)}"
            )

        except FileNotFoundError:

            print(
                f"ERROR: {self.input_file} "
                f"was not found."
            )

            raise

    # =========================================================
    # CHECK REQUIRED COLUMNS
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

            print()
            print(
                "Missing required columns:"
            )

            for column in missing_columns:
                print(
                    f"- {column}"
                )

            raise ValueError(
                "Required columns are missing."
            )

        print()
        print(
            "All required columns are present."
        )

    # =========================================================
    # NUMERIC CLEANING
    # =========================================================

    def prepare_numeric_columns(self):

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

        self.df[
            numeric_columns
        ] = self.df[
            numeric_columns
        ].fillna(0)

        print(
            "Numeric columns prepared."
        )

    # =========================================================
    # SUMMARY STATISTICS
    # =========================================================

    def calculate_statistics(self):

        prices = self.df[
            "Price"
        ].tolist()

        ratings = self.df[
            "Rating"
        ].tolist()

        if prices:

            self.mean_price = statistics.mean(
                prices
            )

            self.median_price = statistics.median(
                prices
            )

            self.minimum_price = min(
                prices
            )

            self.maximum_price = max(
                prices
            )

        else:

            self.mean_price = 0
            self.median_price = 0
            self.minimum_price = 0
            self.maximum_price = 0

        if len(prices) > 1:

            self.price_std = statistics.stdev(
                prices
            )

        else:

            self.price_std = 0

        if ratings:

            self.mean_rating = statistics.mean(
                ratings
            )

            self.minimum_rating = min(
                ratings
            )

            self.maximum_rating = max(
                ratings
            )

        else:

            self.mean_rating = 0
            self.minimum_rating = 0
            self.maximum_rating = 0

        self.price_range = (
            self.maximum_price
            - self.minimum_price
        )

        self.sqrt_max_price = math.sqrt(
            self.maximum_price
        ) if self.maximum_price >= 0 else 0

    # =========================================================
    # NUMPY ANALYSIS
    # =========================================================

    def numpy_analysis(self):

        price_array = self.df[
            "Price"
        ].to_numpy()

        rating_array = self.df[
            "Rating"
        ].to_numpy()

        self.numpy_price_mean = np.mean(
            price_array
        )

        self.numpy_price_std = np.std(
            price_array
        )

        self.numpy_rating_mean = np.mean(
            rating_array
        )

    # =========================================================
    # CATEGORY ANALYSIS
    # =========================================================

    def category_analysis(self):

        self.category_summary = (
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
                Median_Rating=(
                    "Rating",
                    "median"
                ),
                Total_Revenue=(
                    "total_estimated_revenue",
                    "sum"
                )
                if
                "total_estimated_revenue"
                in self.df.columns
                else (
                    "Price",
                    "sum"
                )
            )
            .reset_index()
        )

        self.category_summary[
            "Average_Price"
        ] = self.category_summary[
            "Average_Price"
        ].round(2)

        self.category_summary[
            "Median_Rating"
        ] = self.category_summary[
            "Median_Rating"
        ].round(2)

    # =========================================================
    # TOP PRODUCTS
    # =========================================================

    def find_top_products(self):

        # List comprehension as required
        self.top_product_names = [
            name
            for name in self.df
            .sort_values(
                by="Rating",
                ascending=False
            )
            ["Product Name"]
            .head(10)
            .tolist()
        ]

        self.top_products = (
            self.df
            .sort_values(
                by=[
                    "Rating",
                    "Price"
                ],
                ascending=[
                    False,
                    True
                ]
            )
            .head(10)
        )

    # =========================================================
    # CHART 1
    # BAR CHART - AVERAGE PRICE PER CATEGORY
    # =========================================================

    def create_average_price_bar_chart(self):

        chart_data = (
            self.df
            .groupby("Category")[
                "Price"
            ]
            .mean()
            .sort_values(
                ascending=False
            )
        )

        plt.figure(
            figsize=(10, 6)
        )

        chart_data.plot(
            kind="bar"
        )

        plt.title(
            "Average Price per Category"
        )

        plt.xlabel(
            "Category"
        )

        plt.ylabel(
            "Average Price"
        )

        plt.xticks(
            rotation=45,
            ha="right"
        )

        plt.tight_layout()

        output_file = os.path.join(
            self.charts_folder,
            "average_price_by_category.png"
        )

        plt.savefig(
            output_file,
            dpi=300,
            bbox_inches="tight"
        )

        plt.close()

        print()
        print(
            f"Bar chart saved to: "
            f"{output_file}"
        )

    # =========================================================
    # CHART 2
    # HISTOGRAM - PRODUCT RATINGS
    # =========================================================

    def create_rating_histogram(self):

        ratings = self.df[
            "Rating"
        ].dropna()

        plt.figure(
            figsize=(10, 6)
        )

        plt.hist(
            ratings,
            bins=5,
            edgecolor="black"
        )

        plt.title(
            "Distribution of Product Ratings"
        )

        plt.xlabel(
            "Rating"
        )

        plt.ylabel(
            "Number of Products"
        )

        plt.tight_layout()

        output_file = os.path.join(
            self.charts_folder,
            "rating_histogram.png"
        )

        plt.savefig(
            output_file,
            dpi=300,
            bbox_inches="tight"
        )

        plt.close()

        print()
        print(
            f"Histogram saved to: "
            f"{output_file}"
        )

    # =========================================================
    # CHART 3
    # PLOTLY SCATTER - PRICE VS RATING
    # =========================================================

    def create_price_rating_scatter(self):

        figure = px.scatter(
            self.df,
            x="Price",
            y="Rating",
            hover_name="Product Name",
            title="Price vs Rating",
            labels={
                "Price": "Price",
                "Rating": "Rating"
            }
        )

        output_file = os.path.join(
            self.charts_folder,
            "price_vs_rating.html"
        )

        figure.write_html(
            output_file
        )

        print()
        print(
            f"Interactive scatter plot saved to: "
            f"{output_file}"
        )

    # =========================================================
    # CREATE REQUIRED CHARTS ONLY
    # =========================================================

    def create_visualizations(self):

        print()
        print("=" * 60)
        print("CREATING REQUIRED VISUALIZATIONS")
        print("=" * 60)

        # PDF requires exactly these three types
        self.create_average_price_bar_chart()

        self.create_rating_histogram()

        self.create_price_rating_scatter()

    # =========================================================
    # WRITE ANALYSIS REPORT
    # =========================================================

    def write_report(self):

        category_text = (
            self.category_summary
            .to_string(index=False)
        )

        top_products_text = (
            self.top_products[
                [
                    "Product Name",
                    "Price",
                    "Rating"
                ]
            ]
            .to_string(index=False)
        )

        report_lines = [

            "PRODUCT INSIGHTS THROUGH WEB SCRAPING, "
            "ANALYSIS, AND DATABASE INTEGRATION",

            "",

            "=" * 60,

            "DATASET SUMMARY",

            "=" * 60,

            f"Total Products: {len(self.df)}",

            f"Average Price: "
            f"{self.mean_price:.2f}",

            f"Median Price: "
            f"{self.median_price:.2f}",

            f"Minimum Price: "
            f"{self.minimum_price:.2f}",

            f"Maximum Price: "
            f"{self.maximum_price:.2f}",

            f"Price Standard Deviation: "
            f"{self.price_std:.2f}",

            f"Price Range: "
            f"{self.price_range:.2f}",

            f"Average Rating: "
            f"{self.mean_rating:.2f}",

            f"Minimum Rating: "
            f"{self.minimum_rating:.2f}",

            f"Maximum Rating: "
            f"{self.maximum_rating:.2f}",

            "",

            "=" * 60,

            "NUMPY ANALYSIS",

            "=" * 60,

            f"NumPy Price Mean: "
            f"{self.numpy_price_mean:.2f}",

            f"NumPy Price Standard Deviation: "
            f"{self.numpy_price_std:.2f}",

            f"NumPy Average Rating: "
            f"{self.numpy_rating_mean:.2f}",

            "",

            "=" * 60,

            "CATEGORY SUMMARY",

            "=" * 60,

            category_text,

            "",

            "=" * 60,

            "TOP PRODUCTS",

            "=" * 60,

            top_products_text,

            "",

            "=" * 60,

            "VISUALIZATIONS CREATED",

            "=" * 60,

            "1. Average price per category - "
            "Matplotlib bar chart",

            "2. Product ratings - "
            "Matplotlib histogram",

            "3. Price vs Rating - "
            "Plotly interactive scatter plot",

            "",

            "Charts are stored in the charts folder."
        ]

        with open(
            self.report_file,
            "w",
            encoding="utf-8"
        ) as file:

            file.write(
                "\n".join(report_lines)
            )

        print()
        print(
            f"Analysis report saved to: "
            f"{self.report_file}"
        )

    # =========================================================
    # RUN COMPLETE ANALYSIS
    # =========================================================

    def analyze(self):

        self.load_data()

        self.check_columns()

        self.prepare_numeric_columns()

        self.calculate_statistics()

        self.numpy_analysis()

        self.category_analysis()

        self.find_top_products()

        self.create_visualizations()

        self.write_report()


# =============================================================
# MAIN PROGRAM
# =============================================================

if __name__ == "__main__":

    analyzer = AnalyzerVisualizer(
        input_file="clean_products.csv",
        charts_folder="charts",
        report_file="analysis_summary.txt"
    )

    analyzer.analyze()

    print()
    print("=" * 60)
    print("ANALYSIS AND VISUALIZATION COMPLETED")
    print("=" * 60)

    print()
    print("Created files:")

    print(
        "1. analysis_summary.txt"
    )

    print(
        "2. charts/average_price_by_category.png"
    )

    print(
        "3. charts/rating_histogram.png"
    )

    print(
        "4. charts/price_vs_rating.html"
    )