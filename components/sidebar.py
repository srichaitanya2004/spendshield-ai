"""
SpendShield AI - Sidebar Navigation and Data Upload
"""

import hashlib

import streamlit as st

from services import expense_service


def _get_file_signature(uploaded_file):
    """Create a lightweight signature to detect a new/changed upload."""
    file_bytes = uploaded_file.getvalue()
    return hashlib.md5(file_bytes).hexdigest()


def _reset_analysis_state():
    """Clear AI results because the underlying expense data changed."""
    st.session_state.analysis_done = False
    st.session_state.roast_result = None
    st.session_state.recovery_plan = None


def _load_expense_file(uploaded_file):
    """Validate, clean, and store an uploaded expense CSV."""
    with st.spinner("Processing your expense data..."):
        df = expense_service.load_and_validate_csv(uploaded_file)

        if df is None:
            return False

        cleaned_df = expense_service.clean_data(df)

        if cleaned_df is None or cleaned_df.empty:
            st.error("The uploaded CSV contains no usable expense data.")
            return False

        st.session_state.df_raw = df
        st.session_state.df_cleaned = cleaned_df
        st.session_state.data_loaded = True

        # Track which file is currently loaded.
        st.session_state.uploaded_file_signature = _get_file_signature(
            uploaded_file
        )

        # New data means old AI analysis is no longer valid.
        _reset_analysis_state()

        # Clear any previously extracted receipt.
        st.session_state.receipt_data = None

        return True


def render_sidebar():
    """Render the complete SpendShield AI sidebar."""

    with st.sidebar:
        # ---------------------------------------------------------
        # BRANDING
        # ---------------------------------------------------------
        st.markdown("## 🛡️ SpendShield AI")
        st.caption("AI-powered financial recovery engine")

        st.markdown("---")

        # ---------------------------------------------------------
        # FILE UPLOAD
        # ---------------------------------------------------------
        st.markdown("### 📤 Expense Data")

        uploaded_file = st.file_uploader(
            "Upload your monthly expenses",
            type=["csv"],
            key="expense_csv_uploader",
            help=(
                "CSV should contain: date, description, "
                "category, amount, and type."
            ),
        )

        if uploaded_file is not None:
            current_signature = _get_file_signature(uploaded_file)
            previous_signature = st.session_state.get(
                "uploaded_file_signature"
            )

            # Process only when the user uploads a new/different file.
            if current_signature != previous_signature:
                if _load_expense_file(uploaded_file):
                    st.success("✅ Expense data loaded!")
                    st.rerun()

        # ---------------------------------------------------------
        # NAVIGATION
        # ---------------------------------------------------------
        st.markdown("---")
        st.markdown("### 🧭 Navigate")

        nav_options = [
            ("📊", "Dashboard"),
            ("✏️", "Data Editor"),
            ("🎯", "Budget Simulator"),
            ("📸", "Receipt Scanner"),
        ]

        for icon, option in nav_options:
            is_current = st.session_state.nav_section == option

            label = f"{icon} {option}"

            if st.button(
                label,
                use_container_width=True,
                type="primary" if is_current else "secondary",
                key=f"nav_{option.lower().replace(' ', '_')}",
            ):
                if st.session_state.nav_section != option:
                    st.session_state.nav_section = option
                    st.rerun()

        # ---------------------------------------------------------
        # DATA SUMMARY
        # ---------------------------------------------------------
        if st.session_state.get("data_loaded", False):
            df = st.session_state.df_cleaned

            if df is not None and not df.empty:
                st.markdown("---")
                st.markdown("### 📊 Data Summary")

                total_spending = df["amount"].sum()
                transaction_count = len(df)

                st.metric(
                    "Total Spending",
                    f"₹{total_spending:,.0f}",
                )

                st.metric(
                    "Transactions",
                    f"{transaction_count:,}",
                )

                min_date = df["date"].min()
                max_date = df["date"].max()

                st.caption(
                    f"📅 {min_date:%d %b %Y} → {max_date:%d %b %Y}"
                )