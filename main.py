import os
import sys
import subprocess


class ProjectRunner:

    runner_count = 0

    def __init__(self):
        self.project_folder = os.path.dirname(
            os.path.abspath(__file__)
        )

        self.scripts = [
            "scraper.py",
            "processor.py",
            "analyzer.py",
            "db_handler.py"
        ]

        ProjectRunner.runner_count += 1

    # =========================================================
    # RUN ONE PYTHON SCRIPT
    # =========================================================

    def run_script(self, script_name):

        script_path = os.path.join(
            self.project_folder,
            script_name
        )

        print()
        print("=" * 70)
        print(f"RUNNING: {script_name}")
        print("=" * 70)

        if not os.path.exists(script_path):

            print(
                f"ERROR: {script_name} "
                f"was not found."
            )

            return False

        try:

            result = subprocess.run(
                [
                    sys.executable,
                    script_path
                ],
                cwd=self.project_folder,
                check=False
            )

            if result.returncode != 0:

                print()
                print(
                    f"{script_name} failed."
                )

                print(
                    f"Exit code: "
                    f"{result.returncode}"
                )

                return False

            print()
            print(
                f"{script_name} completed successfully."
            )

            return True

        except Exception as error:

            print()
            print(
                f"Error running {script_name}:"
            )

            print(error)

            return False

    # =========================================================
    # CHECK REQUIRED FILE
    # =========================================================

    def check_file(self, filename):

        file_path = os.path.join(
            self.project_folder,
            filename
        )

        if os.path.exists(file_path):

            print(
                f"Created successfully: "
                f"{filename}"
            )

            return True

        print(
            f"WARNING: {filename} "
            f"was not found."
        )

        return False

    # =========================================================
    # CHECK PROJECT OUTPUTS
    # =========================================================

    def check_outputs(self):

        print()
        print("=" * 70)
        print("CHECKING PROJECT OUTPUTS")
        print("=" * 70)

        required_files = [
            "raw_products.csv",
            "clean_products.csv",
            "analysis_summary.txt"
        ]

        all_files_present = True

        for filename in required_files:

            if not self.check_file(
                filename
            ):
                all_files_present = False

        charts_folder = os.path.join(
            self.project_folder,
            "charts"
        )

        if os.path.isdir(charts_folder):

            chart_files = [
                filename
                for filename in os.listdir(
                    charts_folder
                )
                if filename.lower().endswith(
                    (
                        ".png",
                        ".jpg",
                        ".jpeg",
                        ".html"
                    )
                )
            ]

            print()
            print(
                f"Chart files found: "
                f"{len(chart_files)}"
            )

            for filename in chart_files:

                print(
                    f"  - {filename}"
                )

        else:

            print(
                "WARNING: charts folder "
                "was not found."
            )

            all_files_present = False

        return all_files_present

    # =========================================================
    # RUN COMPLETE PROJECT
    # =========================================================

    def run_project(self):

        print()
        print("=" * 70)
        print(
            "PRODUCT INSIGHTS THROUGH WEB SCRAPING, "
            "ANALYSIS, AND DATABASE INTEGRATION"
        )
        print("=" * 70)

        print()
        print(
            "Python executable:"
        )

        print(
            sys.executable
        )

        print()
        print(
            "Project folder:"
        )

        print(
            self.project_folder
        )

        # -----------------------------------------------------
        # STEP 1 - WEB SCRAPING
        # -----------------------------------------------------

        if not self.run_script(
            "scraper.py"
        ):

            print(
                "Project stopped at "
                "scraping stage."
            )

            return False

        # -----------------------------------------------------
        # STEP 2 - DATA PROCESSING
        # -----------------------------------------------------

        if not self.run_script(
            "processor.py"
        ):

            print(
                "Project stopped at "
                "processing stage."
            )

            return False

        # -----------------------------------------------------
        # STEP 3 - DATA ANALYSIS
        # -----------------------------------------------------

        if not self.run_script(
            "analyzer.py"
        ):

            print(
                "Project stopped at "
                "analysis stage."
            )

            return False

        # -----------------------------------------------------
        # STEP 4 - DATABASE INTEGRATION
        # -----------------------------------------------------

        if not self.run_script(
            "db_handler.py"
        ):

            print(
                "Project stopped at "
                "database stage."
            )

            return False

        # -----------------------------------------------------
        # STEP 5 - CHECK OUTPUTS
        # -----------------------------------------------------

        outputs_ok = (
            self.check_outputs()
        )

        print()
        print("=" * 70)

        if outputs_ok:

            print(
                "PROJECT EXECUTION COMPLETED SUCCESSFULLY."
            )

        else:

            print(
                "PROJECT EXECUTION COMPLETED "
                "WITH OUTPUT WARNINGS."
            )

        print("=" * 70)

        return outputs_ok


# =============================================================
# MAIN PROGRAM
# =============================================================

if __name__ == "__main__":

    runner = ProjectRunner()

    success = runner.run_project()

    if success:

        sys.exit(0)

    sys.exit(1)