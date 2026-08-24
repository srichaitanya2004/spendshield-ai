"""
SpendShield AI - Financial Calculations

Contains all deterministic financial calculations used by the application.

Important:
- Financial calculations are performed locally.
- Gemini is not used for arithmetic.
- Actual savings rate is NOT calculated unless income is available.
- Potential savings is based on a configurable reduction in discretionary spending.
"""

import pandas as pd


# Default assumption used by the recovery engine.
# This means we estimate how much could be saved by reducing
# discretionary spending by 30%.
DEFAULT_DISCRETIONARY_REDUCTION = 0.30


def calculate_metrics(
    df: pd.DataFrame,
    discretionary_reduction: float = DEFAULT_DISCRETIONARY_REDUCTION,
) -> dict:
    """
    Calculate the main financial metrics from expense data.

    Args:
        df: Cleaned expense DataFrame.
        discretionary_reduction: Fraction of discretionary spending
            considered realistically reducible.

    Returns:
        Dictionary containing financial metrics.
    """

    empty_metrics = {
        "total_spending": 0.0,
        "essential": 0.0,
        "discretionary": 0.0,
        "essential_pct": 0.0,
        "discretionary_pct": 0.0,
        "potential_savings": 0.0,
        "potential_savings_rate": 0.0,
        "savings_rate": 0.0,
        "avg_monthly": 0.0,
        "avg_daily": 0.0,
        "transaction_count": 0,
        "date_range_days": 0,
    }

    if df is None or df.empty:
        return empty_metrics

    required_columns = {"amount", "type", "date"}

    if not required_columns.issubset(df.columns):
        return empty_metrics

    # Work on a copy so this function never modifies the original DataFrame.
    data = df.copy()

    # Ensure numeric amounts.
    data["amount"] = pd.to_numeric(
        data["amount"],
        errors="coerce",
    )

    # Remove invalid transactions.
    data = data.dropna(subset=["amount", "date"])

    if data.empty:
        return empty_metrics

    # Make sure dates are datetime objects.
    data["date"] = pd.to_datetime(
        data["date"],
        errors="coerce",
    )

    data = data.dropna(subset=["date"])

    if data.empty:
        return empty_metrics

    # ---------------------------------------------------------
    # TOTAL SPENDING
    # ---------------------------------------------------------

    total_spending = float(data["amount"].sum())

    # ---------------------------------------------------------
    # ESSENTIAL VS DISCRETIONARY
    # ---------------------------------------------------------

    essential = float(
        data.loc[
            data["type"].astype(str).str.strip().str.lower() == "essential",
            "amount",
        ].sum()
    )

    discretionary = float(
        data.loc[
            data["type"].astype(str).str.strip().str.lower()
            == "discretionary",
            "amount",
        ].sum()
    )

    # ---------------------------------------------------------
    # SPENDING PERCENTAGES
    # ---------------------------------------------------------

    if total_spending > 0:
        essential_pct = (essential / total_spending) * 100
        discretionary_pct = (discretionary / total_spending) * 100
    else:
        essential_pct = 0.0
        discretionary_pct = 0.0

    # ---------------------------------------------------------
    # POTENTIAL SAVINGS
    # ---------------------------------------------------------
    #
    # We do NOT claim this is the user's actual savings.
    #
    # Instead:
    #
    # potential savings =
    # discretionary spending × reduction target
    #
    # Example:
    # ₹10,000 discretionary × 30% = ₹3,000 potential savings
    #

    discretionary_reduction = max(
        0.0,
        min(float(discretionary_reduction), 1.0),
    )

    potential_savings = discretionary * discretionary_reduction

    if total_spending > 0:
        potential_savings_rate = (
            potential_savings / total_spending
        ) * 100
    else:
        potential_savings_rate = 0.0

    # Keep this key for compatibility with the existing dashboard.
    #
    # IMPORTANT:
    # This is NOT the user's real savings rate.
    # It represents the estimated savings opportunity.
    savings_rate = potential_savings_rate

    # ---------------------------------------------------------
    # DATE RANGE
    # ---------------------------------------------------------

    min_date = data["date"].min()
    max_date = data["date"].max()

    date_range_days = max(
        1,
        (max_date - min_date).days + 1,
    )

    # ---------------------------------------------------------
    # AVERAGE SPENDING
    # ---------------------------------------------------------

    avg_daily = total_spending / date_range_days

    # Approximate monthly spending using a 30-day month.
    avg_monthly = avg_daily * 30

    # ---------------------------------------------------------
    # TRANSACTION COUNT
    # ---------------------------------------------------------

    transaction_count = len(data)

    return {
        "total_spending": total_spending,
        "essential": essential,
        "discretionary": discretionary,
        "essential_pct": essential_pct,
        "discretionary_pct": discretionary_pct,
        "potential_savings": potential_savings,
        "potential_savings_rate": potential_savings_rate,

        # Kept for compatibility with existing components.
        "savings_rate": savings_rate,

        "avg_monthly": avg_monthly,
        "avg_daily": avg_daily,
        "transaction_count": transaction_count,
        "date_range_days": date_range_days,
    }


def calculate_category_stats(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate spending statistics grouped by category.

    Returns:
        DataFrame containing:
        - total
        - average
        - count
        - percentage
    """

    if df is None or df.empty:
        return pd.DataFrame(
            columns=[
                "total",
                "average",
                "count",
                "percentage",
            ]
        )

    required_columns = {"category", "amount"}

    if not required_columns.issubset(df.columns):
        return pd.DataFrame(
            columns=[
                "total",
                "average",
                "count",
                "percentage",
            ]
        )

    data = df.copy()

    data["amount"] = pd.to_numeric(
        data["amount"],
        errors="coerce",
    )

    data = data.dropna(
        subset=["category", "amount"]
    )

    if data.empty:
        return pd.DataFrame(
            columns=[
                "total",
                "average",
                "count",
                "percentage",
            ]
        )

    # Group spending by category.
    stats = (
        data.groupby("category")["amount"]
        .agg(
            total="sum",
            average="mean",
            count="count",
        )
        .sort_values(
            "total",
            ascending=False,
        )
    )

    total = stats["total"].sum()

    if total > 0:
        stats["percentage"] = (
            stats["total"] / total
        ) * 100
    else:
        stats["percentage"] = 0.0

    # Keep numeric output clean.
    stats["total"] = stats["total"].round(2)
    stats["average"] = stats["average"].round(2)
    stats["percentage"] = stats["percentage"].round(1)

    return stats