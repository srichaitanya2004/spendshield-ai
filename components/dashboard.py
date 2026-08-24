"""
SpendShield AI - Dashboard KPI Components
"""

import streamlit as st

from utils import calculations


def render_kpi_row(df):
    """Render the main financial KPI cards."""

    metrics = calculations.calculate_metrics(df)

    col1, col2, col3, col4 = st.columns(4)

    # ---------------------------------------------------------
    # TOTAL SPENDING
    # ---------------------------------------------------------
    with col1:
        st.metric(
            label="💰 Total Spending",
            value=f"₹{metrics['total_spending']:,.0f}",
            delta=f"₹{metrics['avg_monthly']:,.0f} avg/month",
            delta_color="off",
            help="Total amount spent across all recorded transactions.",
        )

    # ---------------------------------------------------------
    # DISCRETIONARY SPENDING
    # ---------------------------------------------------------
    with col2:
        discretionary_pct = metrics["discretionary_pct"]

        st.metric(
            label="🎯 Discretionary Spend",
            value=f"₹{metrics['discretionary']:,.0f}",
            delta=f"{discretionary_pct:.1f}% of spending",
            delta_color="inverse",
            help=(
                "Money spent on non-essential categories. "
                "Reducing this is usually the fastest route to savings."
            ),
        )

    # ---------------------------------------------------------
    # POTENTIAL SAVINGS
    # ---------------------------------------------------------
    with col3:
        monthly_savings = metrics["potential_savings"]
        annual_savings = monthly_savings * 12

        st.metric(
            label="💎 Potential Savings",
            value=f"₹{monthly_savings:,.0f}",
            delta=f"₹{annual_savings:,.0f}/year",
            delta_color="normal",
            help=(
                "Estimated monthly savings opportunity based on "
                "your discretionary spending."
            ),
        )

    # ---------------------------------------------------------
    # SAVINGS RATE
    # ---------------------------------------------------------
    with col4:
        savings_rate = metrics["savings_rate"]

        if savings_rate >= 20:
            status = "🟢 Healthy"
        elif savings_rate >= 10:
            status = "🟡 Moderate"
        else:
            status = "🔴 Needs attention"

        st.metric(
            label="📈 Savings Rate",
            value=f"{savings_rate:.1f}%",
            delta=status,
            delta_color="off",
            help=(
                "Estimated percentage of income available for savings. "
                "The status is based on the configured financial target."
            ),
        )