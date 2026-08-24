"""
SpendShield AI - Expense Data Service

Handles:
- CSV loading
- Data validation
- Data cleaning
- Sample/demo data

The service layer performs data operations and returns structured
results. UI-specific messages are handled by the Streamlit components.
"""

import pandas as pd

from utils import data_cleaning


# Required columns for the SpendShield expense schema.
REQUIRED_COLUMNS = [
    "date",
    "description",
    "category",
    "amount",
    "type",
]


# ---------------------------------------------------------
# CSV LOADING
# ---------------------------------------------------------

def load_and_validate_csv(file):
    """
    Load an uploaded CSV and validate its structure.

    Args:
        file: Streamlit UploadedFile or file-like object.

    Returns:
        tuple:
            (DataFrame, validation_result)

        If loading fails:
            (None, validation_result)
    """

    try:
        df = pd.read_csv(file)

    except Exception as exc:
        return None, {
            "is_valid": False,
            "errors": [
                f"Could not read the CSV file: {exc}"
            ],
            "warnings": [],
        }

    # -----------------------------------------------------
    # BASIC FILE VALIDATION
    # -----------------------------------------------------

    if df.empty:
        return None, {
            "is_valid": False,
            "errors": ["The uploaded CSV contains no rows."],
            "warnings": [],
        }

    # Normalize column names.
    df.columns = (
        df.columns
        .astype(str)
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )

    # -----------------------------------------------------
    # REQUIRED COLUMNS
    # -----------------------------------------------------

    missing_columns = [
        column
        for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    if missing_columns:
        return None, {
            "is_valid": False,
            "errors": [
                "Missing required columns: "
                + ", ".join(missing_columns)
            ],
            "warnings": [],
        }

    # -----------------------------------------------------
    # VALIDATE DATA
    # -----------------------------------------------------

    validation_result = data_cleaning.validate_dataframe(df)

    if not validation_result["is_valid"]:
        return None, validation_result

    return df, validation_result


# ---------------------------------------------------------
# DATA CLEANING
# ---------------------------------------------------------

def clean_data(df):
    """
    Clean and standardize an expense DataFrame.

    The pipeline intentionally does not silently delete
    statistical outliers. Unusual transactions are flagged
    separately by detect_anomalies().

    Args:
        df: Raw expense DataFrame.

    Returns:
        Cleaned DataFrame.
    """

    if df is None or df.empty:
        return pd.DataFrame()

    clean_df = df.copy()

    # -----------------------------------------------------
    # REMOVE EXACT DUPLICATES
    # -----------------------------------------------------

    clean_df = clean_df.drop_duplicates().reset_index(drop=True)

    # -----------------------------------------------------
    # CLEAN AMOUNTS
    # -----------------------------------------------------

    clean_df = data_cleaning.clean_amounts(
        clean_df,
        "amount",
    )

    # Remove rows where amount cannot be interpreted.
    clean_df = clean_df.dropna(
        subset=["amount"]
    )

    # Expenses must have a positive amount.
    #
    # Negative values may represent refunds/credits.
    # For the current expense-only product, we exclude them
    # rather than silently converting them to positive expenses.
    clean_df = clean_df[
        clean_df["amount"] > 0
    ]

    # -----------------------------------------------------
    # CLEAN DATES
    # -----------------------------------------------------

    clean_df = data_cleaning.clean_dates(
        clean_df,
        "date",
    )

    # -----------------------------------------------------
    # CLEAN TEXT FIELDS
    # -----------------------------------------------------

    clean_df = data_cleaning.clean_descriptions(
        clean_df,
        "description",
    )

    clean_df = data_cleaning.clean_categories(
        clean_df,
        "category",
    )

    clean_df = data_cleaning.clean_types(
        clean_df,
        "type",
    )

    # -----------------------------------------------------
    # HANDLE MISSING VALUES
    # -----------------------------------------------------

    clean_df = data_cleaning.handle_missing_values(
        clean_df
    )

    # -----------------------------------------------------
    # DATE FEATURES
    # -----------------------------------------------------

    clean_df = data_cleaning.create_date_features(
        clean_df
    )

    # -----------------------------------------------------
    # ANOMALY FLAGS
    # -----------------------------------------------------

    clean_df = data_cleaning.detect_anomalies(
        clean_df
    )

    # -----------------------------------------------------
    # FINAL SORT
    # -----------------------------------------------------

    if "date" in clean_df.columns:
        clean_df = clean_df.sort_values(
            "date"
        ).reset_index(drop=True)

    return clean_df


# ---------------------------------------------------------
# DATASET SUMMARY
# ---------------------------------------------------------

def get_data_summary(df):
    """
    Return a compact summary of an expense dataset.

    Useful for UI messages and AI context.
    """

    if df is None or df.empty:
        return {
            "rows": 0,
            "total_spending": 0.0,
            "categories": 0,
            "date_start": None,
            "date_end": None,
        }

    return {
        "rows": len(df),
        "total_spending": float(
            df["amount"].sum()
        ),
        "categories": (
            df["category"].nunique()
            if "category" in df.columns
            else 0
        ),
        "date_start": (
            df["date"].min()
            if "date" in df.columns
            else None
        ),
        "date_end": (
            df["date"].max()
            if "date" in df.columns
            else None
        ),
    }


# ---------------------------------------------------------
# SAMPLE DATA
# ---------------------------------------------------------

def get_sample_data():
    """
    Generate realistic sample expense data for demos/testing.

    Returns:
        pd.DataFrame
    """

    sample_data = {
        "date": pd.date_range(
            start="2026-01-01",
            periods=30,
            freq="D",
        ),

        "description": [
            "Netflix",
            "Rent",
            "Uber",
            "Groceries",
            "Dinner Out",
            "Amazon",
            "Utilities",
            "Coffee",
            "Gas",
            "Gym",
            "Spotify",
            "Shopping",
            "Phone Bill",
            "Groceries",
            "Movie",
            "Uber Eats",
            "Rent",
            "Netflix",
            "Groceries",
            "Dining",
            "Amazon",
            "Coffee",
            "Gas",
            "Groceries",
            "Uber",
            "Shopping",
            "Phone Bill",
            "Groceries",
            "Dinner",
            "Netflix",
        ],

        "category": [
            "Entertainment",
            "Housing",
            "Transport",
            "Food",
            "Dining",
            "Shopping",
            "Utilities",
            "Food",
            "Transport",
            "Health",
            "Entertainment",
            "Shopping",
            "Utilities",
            "Food",
            "Entertainment",
            "Dining",
            "Housing",
            "Entertainment",
            "Food",
            "Dining",
            "Shopping",
            "Food",
            "Transport",
            "Food",
            "Transport",
            "Shopping",
            "Utilities",
            "Food",
            "Dining",
            "Entertainment",
        ],

        "amount": [
            649,
            15000,
            450,
            3200,
            1200,
            2500,
            1000,
            150,
            500,
            800,
            199,
            1800,
            500,
            2500,
            600,
            750,
            15000,
            649,
            2800,
            950,
            3000,
            120,
            550,
            2100,
            380,
            2200,
            500,
            2700,
            1400,
            649,
        ],

        "type": [
            "Discretionary",
            "Essential",
            "Discretionary",
            "Essential",
            "Discretionary",
            "Discretionary",
            "Essential",
            "Discretionary",
            "Essential",
            "Essential",
            "Discretionary",
            "Discretionary",
            "Essential",
            "Essential",
            "Discretionary",
            "Discretionary",
            "Essential",
            "Discretionary",
            "Essential",
            "Discretionary",
            "Discretionary",
            "Discretionary",
            "Essential",
            "Essential",
            "Discretionary",
            "Discretionary",
            "Essential",
            "Essential",
            "Discretionary",
            "Discretionary",
        ],
    }

    return pd.DataFrame(sample_data)


# ---------------------------------------------------------
# COMPLETE SAMPLE-DATA PIPELINE
# ---------------------------------------------------------

def get_clean_sample_data():
    """
    Return cleaned and enriched demo data.

    Useful when the application needs a ready-to-display
    dataset without going through CSV upload.
    """

    sample_df = get_sample_data()

    return clean_data(sample_df)