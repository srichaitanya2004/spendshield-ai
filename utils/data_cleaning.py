"""
SpendShield AI - Data Cleaning and Validation Utilities

This module handles:
- Amount cleaning
- Date normalization
- Category normalization
- Description cleaning
- Missing-value handling
- Data validation
- Date feature creation
- Anomaly detection

Important:
Cleaning should improve data quality without silently deleting
legitimate financial transactions.
"""

import pandas as pd


# ---------------------------------------------------------
# AMOUNT CLEANING
# ---------------------------------------------------------

def clean_amounts(df, amount_column="amount"):
    """
    Clean and standardize expense amounts.

    Currency symbols and commas are removed.
    Invalid values become NaN and can be handled by validation.

    Negative values are preserved so that the application does not
    silently convert refunds/credits into expenses.

    Args:
        df: Input DataFrame.
        amount_column: Name of the amount column.

    Returns:
        Cleaned DataFrame.
    """

    df = df.copy()

    if amount_column not in df.columns:
        return df

    # Convert everything to string first so values such as
    # "₹1,250" and "$1,250" can be handled consistently.
    df[amount_column] = (
        df[amount_column]
        .astype(str)
        .str.strip()
        .str.replace(r"[₹$€£,]", "", regex=True)
        .str.replace(r"^\((.*)\)$", r"-\1", regex=True)
    )

    df[amount_column] = pd.to_numeric(
        df[amount_column],
        errors="coerce",
    )

    return df


# ---------------------------------------------------------
# DATE CLEANING
# ---------------------------------------------------------

def clean_dates(df, date_column="date"):
    """
    Convert the date column into pandas datetime values.

    Invalid dates are removed because a transaction without
    a valid date cannot be reliably used for time-based analysis.

    Future dates are removed because the application analyzes
    historical/current expenses.

    Args:
        df: Input DataFrame.
        date_column: Name of the date column.

    Returns:
        DataFrame with standardized dates.
    """

    df = df.copy()

    if date_column not in df.columns:
        return df

    df[date_column] = pd.to_datetime(
        df[date_column],
        errors="coerce",
        dayfirst=False,
    )

    # Remove invalid dates.
    df = df.dropna(subset=[date_column])

    # Normalize timestamps to midnight.
    df[date_column] = df[date_column].dt.normalize()

    # Prevent future transactions from entering historical
    # spending analysis.
    today = pd.Timestamp.now().normalize()

    df = df[df[date_column] <= today]

    return df


# ---------------------------------------------------------
# CATEGORY CLEANING
# ---------------------------------------------------------

def clean_categories(df, category_column="category"):
    """
    Normalize common category variations.

    Unknown categories are preserved rather than discarded.
    """

    df = df.copy()

    if category_column not in df.columns:
        return df

    category_mapping = {
        "groceries": "Food",
        "grocery": "Food",
        "food": "Food",

        "restaurant": "Dining",
        "restaurants": "Dining",
        "dining": "Dining",
        "eat out": "Dining",
        "takeout": "Dining",
        "takeaway": "Dining",
        "delivery": "Dining",

        "uber": "Transport",
        "lyft": "Transport",
        "taxi": "Transport",
        "cab": "Transport",
        "gas": "Transport",
        "fuel": "Transport",
        "petrol": "Transport",

        "rent": "Housing",
        "mortgage": "Housing",

        "utilities": "Utilities",
        "electric": "Utilities",
        "electricity": "Utilities",
        "water": "Utilities",
        "internet": "Utilities",
        "phone": "Utilities",

        "netflix": "Entertainment",
        "spotify": "Entertainment",
        "movies": "Entertainment",
        "gaming": "Entertainment",

        "amazon": "Shopping",
        "walmart": "Shopping",
        "target": "Shopping",
        "clothing": "Shopping",
        "shoes": "Shopping",

        "gym": "Health",
        "doctor": "Health",
        "pharmacy": "Health",
        "medicine": "Health",

        "hotel": "Travel",
        "flight": "Travel",
        "airline": "Travel",

        "insurance": "Insurance",
        "education": "Education",
        "school": "Education",
        "college": "Education",
    }

    # Convert missing categories into "Other".
    df[category_column] = (
        df[category_column]
        .fillna("Other")
        .astype(str)
        .str.strip()
    )

    # Normalize lookup key while preserving a clean display name.
    normalized = df[category_column].str.lower()

    df[category_column] = normalized.map(
        lambda value: category_mapping.get(
            value,
            value.title(),
        )
    )

    return df


# ---------------------------------------------------------
# DESCRIPTION CLEANING
# ---------------------------------------------------------

def clean_descriptions(df, description_column="description"):
    """
    Clean expense descriptions without destroying useful information.
    """

    df = df.copy()

    if description_column not in df.columns:
        return df

    df[description_column] = (
        df[description_column]
        .fillna("Unknown Expense")
        .astype(str)
        .str.strip()
        .str.replace(r"\s+", " ", regex=True)
    )

    # Replace blank strings after cleaning.
    df.loc[
        df[description_column].eq(""),
        description_column,
    ] = "Unknown Expense"

    return df


# ---------------------------------------------------------
# MISSING VALUES
# ---------------------------------------------------------

def handle_missing_values(df):
    """
    Handle missing values while preserving useful transaction data.
    """

    df = df.copy()

    if "category" in df.columns:
        df["category"] = df["category"].fillna("Other")

    if "type" in df.columns:
        df["type"] = df["type"].fillna("Discretionary")

    if "description" in df.columns:
        df["description"] = (
            df["description"]
            .fillna("Unknown Expense")
        )

    # Transactions without a valid amount cannot be analyzed.
    if "amount" in df.columns:
        df = df.dropna(subset=["amount"])

    return df


# ---------------------------------------------------------
# TYPE NORMALIZATION
# ---------------------------------------------------------

def clean_types(df, type_column="type"):
    """
    Normalize Essential / Discretionary transaction types.
    """

    df = df.copy()

    if type_column not in df.columns:
        # If the column doesn't exist, default to discretionary.
        df[type_column] = "Discretionary"
        return df

    df[type_column] = (
        df[type_column]
        .fillna("Discretionary")
        .astype(str)
        .str.strip()
        .str.lower()
    )

    type_mapping = {
        "essential": "Essential",
        "necessity": "Essential",
        "necessary": "Essential",
        "fixed": "Essential",

        "discretionary": "Discretionary",
        "optional": "Discretionary",
        "luxury": "Discretionary",
        "non-essential": "Discretionary",
        "nonessential": "Discretionary",
    }

    df[type_column] = df[type_column].map(
        lambda value: type_mapping.get(
            value,
            "Discretionary",
        )
    )

    return df


# ---------------------------------------------------------
# VALIDATION
# ---------------------------------------------------------

def validate_dataframe(df):
    """
    Perform comprehensive validation of an expense DataFrame.

    Returns:
        Dictionary containing:
        - is_valid
        - errors
        - warnings
    """

    validation_result = {
        "is_valid": True,
        "errors": [],
        "warnings": [],
    }

    # -----------------------------------------------------
    # BASIC VALIDATION
    # -----------------------------------------------------

    if df is None:
        return {
            "is_valid": False,
            "errors": ["No dataframe was provided."],
            "warnings": [],
        }

    if df.empty:
        validation_result["is_valid"] = False
        validation_result["errors"].append(
            "The uploaded CSV is empty."
        )
        return validation_result

    # -----------------------------------------------------
    # REQUIRED COLUMNS
    # -----------------------------------------------------

    required_columns = [
        "date",
        "description",
        "category",
        "amount",
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        validation_result["is_valid"] = False

        validation_result["errors"].append(
            "Missing required columns: "
            + ", ".join(missing_columns)
        )

        return validation_result

    # -----------------------------------------------------
    # AMOUNT VALIDATION
    # -----------------------------------------------------

    if "amount" in df.columns:

        numeric_amounts = pd.to_numeric(
            df["amount"],
            errors="coerce",
        )

        invalid_amounts = numeric_amounts.isna().sum()

        if invalid_amounts > 0:
            validation_result["warnings"].append(
                f"{invalid_amounts} transaction(s) have "
                "invalid or missing amounts and will be removed."
            )

        negative_amounts = (
            numeric_amounts < 0
        ).sum()

        if negative_amounts > 0:
            validation_result["warnings"].append(
                f"{negative_amounts} negative transaction(s) "
                "were found. Review them because they may represent "
                "refunds or credits."
            )

        zero_amounts = (
            numeric_amounts == 0
        ).sum()

        if zero_amounts > 0:
            validation_result["warnings"].append(
                f"{zero_amounts} transaction(s) have zero amount "
                "and will be removed."
            )

        unusually_large = (
            numeric_amounts > 1_000_000
        ).sum()

        if unusually_large > 0:
            validation_result["warnings"].append(
                f"{unusually_large} transaction(s) exceed "
                "₹1,000,000. Please verify these amounts."
            )

    # -----------------------------------------------------
    # DATE VALIDATION
    # -----------------------------------------------------

    if "date" in df.columns:

        parsed_dates = pd.to_datetime(
            df["date"],
            errors="coerce",
        )

        invalid_dates = parsed_dates.isna().sum()

        if invalid_dates > 0:
            validation_result["warnings"].append(
                f"{invalid_dates} transaction(s) have invalid "
                "dates and will be removed."
            )

        future_dates = (
            parsed_dates
            > pd.Timestamp.now()
        ).sum()

        if future_dates > 0:
            validation_result["warnings"].append(
                f"{future_dates} transaction(s) contain future "
                "dates and will be removed."
            )

    # -----------------------------------------------------
    # TYPE VALIDATION
    # -----------------------------------------------------

    if "type" in df.columns:

        normalized_types = (
            df["type"]
            .fillna("")
            .astype(str)
            .str.strip()
            .str.lower()
        )

        valid_types = {
            "essential",
            "discretionary",
        }

        invalid_types = ~normalized_types.isin(
            valid_types
        )

        invalid_count = invalid_types.sum()

        if invalid_count > 0:
            validation_result["warnings"].append(
                f"{invalid_count} transaction(s) have an "
                "unrecognized type and will be classified as "
                "Discretionary."
            )

    return validation_result


# ---------------------------------------------------------
# DATE FEATURES
# ---------------------------------------------------------

def create_date_features(df):
    """
    Create useful date-based features for analysis and charts.
    """

    df = df.copy()

    if "date" not in df.columns:
        return df

    if not pd.api.types.is_datetime64_any_dtype(
        df["date"]
    ):
        df["date"] = pd.to_datetime(
            df["date"],
            errors="coerce",
        )

    df["year"] = df["date"].dt.year
    df["month"] = df["date"].dt.month
    df["day"] = df["date"].dt.day
    df["day_of_week"] = df["date"].dt.day_name()
    df["weekend"] = (
        df["date"].dt.dayofweek >= 5
    )
    df["quarter"] = df["date"].dt.quarter

    df["month_name"] = (
        df["date"].dt.month_name()
    )

    # Useful for chronological charts.
    df["year_month"] = (
        df["date"]
        .dt.to_period("M")
        .astype(str)
    )

    return df


# ---------------------------------------------------------
# ANOMALY DETECTION
# ---------------------------------------------------------

def detect_anomalies(df):
    """
    Detect unusually large transactions.

    Anomalies are FLAGGED rather than deleted.

    Returns:
        DataFrame with:
        - z_score
        - is_anomaly
    """

    df = df.copy()

    if "amount" not in df.columns:
        return df

    if len(df) < 3:
        df["z_score"] = 0.0
        df["is_anomaly"] = False
        return df

    amounts = pd.to_numeric(
        df["amount"],
        errors="coerce",
    )

    mean = amounts.mean()
    std = amounts.std()

    if pd.isna(std) or std == 0:
        df["z_score"] = 0.0
        df["is_anomaly"] = False
        return df

    df["z_score"] = (
        (amounts - mean) / std
    ).round(2)

    df["is_anomaly"] = (
        df["z_score"].abs() > 3
    )

    return df