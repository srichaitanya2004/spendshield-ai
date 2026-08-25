"""
SpendShield AI
AI-powered personal finance intelligence dashboard.

Main application entry point.
"""

import hashlib
from datetime import datetime

import pandas as pd
import streamlit as st

from components import charts, budget_simulator
from services import expense_service, gemini_service
from utils import calculations


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="SpendShield AI",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# CUSTOM STYLING
# ============================================================

st.markdown(
    """
<style>

.main {
    padding: 1rem 2rem 3rem 2rem;
}

.block-container {
    max-width: 1500px;
    padding-top: 2rem;
}

[data-testid="stSidebar"] {
    border-right: 1px solid rgba(128, 128, 128, 0.15);
}

[data-testid="stMetric"] {
    background: rgba(128, 128, 128, 0.06);
    border: 1px solid rgba(128, 128, 128, 0.15);
    padding: 1rem;
    border-radius: 14px;
}

.hero-container {
    padding: 1rem 0 0.5rem 0;
}

.hero-title {
    font-size: clamp(2.2rem, 5vw, 3.5rem);
    font-weight: 800;
    letter-spacing: -1px;
    margin-bottom: 0;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.hero-subtitle {
    font-size: 1.1rem;
    opacity: 0.7;
    margin-top: 0.25rem;
}

.section-title {
    font-size: 1.5rem;
    font-weight: 700;
    margin-top: 1rem;
}

.section-description {
    opacity: 0.7;
    margin-bottom: 1rem;
}

.custom-divider {
    border: none;
    height: 2px;
    background: linear-gradient(
        90deg,
        #667eea 0%,
        #764ba2 50%,
        transparent 100%
    );
    margin: 1.5rem 0;
}

.ai-card {
    padding: 1.4rem;
    border-radius: 16px;
    border: 1px solid rgba(102, 126, 234, 0.25);
    background: linear-gradient(
        135deg,
        rgba(102, 126, 234, 0.08),
        rgba(118, 75, 162, 0.08)
    );
    margin: 0.5rem 0 1rem 0;
}

.health-score {
    text-align: center;
    padding: 1.5rem;
    border-radius: 18px;
    border: 1px solid rgba(128, 128, 128, 0.15);
}

</style>
""",
    unsafe_allow_html=True
)


# ============================================================
# SESSION STATE
# ============================================================

def init_session_state():
    """Initialize all application session-state variables."""

    defaults = {
        "data_loaded": False,
        "df_raw": None,
        "df_cleaned": None,

        "analysis_done": False,
        "roast_result": None,
        "recovery_plan": None,

        "receipt_data": None,

        "budget_sim": {},

        "nav_section": "Dashboard",

        "uploaded_file_id": None,

        "data_version": None,

        "analysis_version": None,
        "analysis_timestamp": None,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


init_session_state()


# ============================================================
# HELPERS
# ============================================================

def dataframe_signature(df):
    """Create a simple signature for dataframe version tracking."""

    if df is None or df.empty:
        return "empty"

    try:
        data_string = df.to_csv(index=False)
        return hashlib.md5(
            data_string.encode("utf-8")
        ).hexdigest()

    except Exception:
        return str(len(df))


def format_currency(value):
    """Format Indian Rupee values."""

    try:
        return f"₹{float(value):,.0f}"
    except (TypeError, ValueError):
        return "₹0"


def invalidate_analysis():
    """Invalidate previous AI results."""

    st.session_state.analysis_done = False
    st.session_state.roast_result = None
    st.session_state.recovery_plan = None
    st.session_state.analysis_version = None
    st.session_state.analysis_timestamp = None


def update_data(df):
    """Update dataframe and invalidate stale AI analysis."""

    if df is None:
        st.session_state.df_cleaned = None
        st.session_state.data_version = None
        invalidate_analysis()
        return

    st.session_state.df_cleaned = df.copy()
    st.session_state.data_version = dataframe_signature(df)

    invalidate_analysis()


def get_financial_health_score(metrics):
    """
    Calculate an approximate spending-health score.

    This is based only on spending behavior because income,
    debt, investments and savings balances are not available.
    """

    discretionary_pct = metrics.get(
        "discretionary_pct",
        0
    )

    score = 100

    if discretionary_pct > 60:
        score -= 35

    elif discretionary_pct > 50:
        score -= 25

    elif discretionary_pct > 40:
        score -= 15

    elif discretionary_pct > 30:
        score -= 8

    return max(
        0,
        min(100, score)
    )


def health_label(score):
    """Return health label."""

    if score >= 85:
        return "Excellent"

    if score >= 70:
        return "Healthy"

    if score >= 50:
        return "Needs Attention"

    return "High Risk"


# ============================================================
# SIDEBAR
# ============================================================

def render_sidebar():
    """Render the application sidebar safely."""

    with st.sidebar:

        st.markdown(
            '<div class="sidebar-brand">'
            '🛡️ SpendShield AI'
            '</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            '<div class="sidebar-caption">'
            'AI-powered personal finance intelligence'
            '</div>',
            unsafe_allow_html=True
        )

        st.markdown("---")

        # ----------------------------------------------------
        # FILE UPLOAD
        # ----------------------------------------------------

        st.markdown("#### 📤 Import Expenses")

        uploaded_file = st.file_uploader(
            "Upload your expense CSV",
            type=["csv"],
            help=(
                "Required columns: date, description, "
                "category, amount, type"
            ),
            key="expense_csv_uploader"
        )

        if uploaded_file is not None:

            file_id = (
                f"{uploaded_file.name}_"
                f"{uploaded_file.size}"
            )

            previous_file_id = st.session_state.get(
                "uploaded_file_id"
            )

            if previous_file_id != file_id:

                with st.spinner(
                    "🔄 Processing your expenses..."
                ):

                    try:

                        df = (
                            expense_service
                            .load_and_validate_csv(
                                uploaded_file
                            )
                        )

                    except Exception as e:

                        st.error(
                            f"CSV processing failed: {str(e)}"
                        )

                        df = None

                    if df is None:

                        st.error(
                            "❌ Could not load the CSV file."
                        )

                    elif not isinstance(df, pd.DataFrame):

                        st.error(
                            "❌ The CSV loader did not return "
                            "a valid dataframe."
                        )

                    elif df.empty:

                        st.error(
                            "❌ The uploaded CSV contains "
                            "no rows."
                        )

                    else:

                        try:

                            cleaned_df = (
                                expense_service
                                .clean_data(df)
                            )

                        except Exception as e:

                            st.error(
                                f"Data cleaning failed: {str(e)}"
                            )

                            cleaned_df = None

                        if (
                            cleaned_df is None
                            or not isinstance(
                                cleaned_df,
                                pd.DataFrame
                            )
                            or cleaned_df.empty
                        ):

                            st.error(
                                "❌ The file contains no valid "
                                "expense transactions after "
                                "cleaning."
                            )

                        else:

                            st.session_state.df_raw = (
                                df.copy()
                            )

                            update_data(
                                cleaned_df
                            )

                            st.session_state.data_loaded = True

                            st.session_state.uploaded_file_id = (
                                file_id
                            )

                            st.session_state.receipt_data = None

                            st.success(
                                "✅ Expenses imported successfully."
                            )

                            st.rerun()

        # ----------------------------------------------------
        # DEMO DATA
        # ----------------------------------------------------

        st.markdown("##### Or explore the demo")

        if st.button(
            "✨ Load Demo Expenses",
            use_container_width=True,
            key="load_demo"
        ):

            try:

                demo_df = (
                    expense_service
                    .get_sample_data()
                )

                if (
                    demo_df is not None
                    and not demo_df.empty
                ):

                    update_data(
                        demo_df
                    )

                    st.session_state.df_raw = (
                        demo_df.copy()
                    )

                    st.session_state.data_loaded = True

                    st.session_state.uploaded_file_id = (
                        "demo"
                    )

                    st.rerun()

                else:

                    st.error(
                        "Demo dataset is empty."
                    )

            except Exception as e:

                st.error(
                    f"Could not load demo data: {str(e)}"
                )

        # ----------------------------------------------------
        # NAVIGATION
        # ----------------------------------------------------

        st.markdown("---")
        st.markdown("#### 🧭 Navigation")

        nav_options = [
            ("📊", "Dashboard"),
            ("✏️", "Data Editor"),
            ("🎯", "Budget Simulator"),
            ("📸", "Receipt Scanner"),
        ]

        for icon, option in nav_options:

            label = f"{icon} {option}"

            button_type = (
                "primary"
                if st.session_state.nav_section == option
                else "secondary"
            )

            if st.button(
                label,
                use_container_width=True,
                type=button_type,
                key=f"nav_{option}"
            ):

                if (
                    st.session_state.nav_section
                    != option
                ):

                    st.session_state.nav_section = (
                        option
                    )

                    st.rerun()

        # ----------------------------------------------------
        # DATA SUMMARY
        # ----------------------------------------------------

        if st.session_state.get(
            "data_loaded",
            False
        ):

            df = st.session_state.get(
                "df_cleaned"
            )

            # IMPORTANT:
            # Never access df.empty or df["amount"]
            # until we know df is a real dataframe.

            if (
                df is not None
                and isinstance(df, pd.DataFrame)
                and not df.empty
            ):

                st.markdown("---")
                st.markdown("#### 📊 Dataset")

                if "amount" in df.columns:

                    try:

                        total = pd.to_numeric(
                            df["amount"],
                            errors="coerce"
                        ).sum()

                        st.metric(
                            "Total Spending",
                            format_currency(total)
                        )

                    except Exception:

                        st.metric(
                            "Total Spending",
                            "₹0"
                        )

                else:

                    st.metric(
                        "Total Spending",
                        "₹0"
                    )

                st.metric(
                    "Transactions",
                    f"{len(df):,}"
                )

                if "date" in df.columns:

                    try:

                        dates = pd.to_datetime(
                            df["date"],
                            errors="coerce"
                        ).dropna()

                        if not dates.empty:

                            start_date = (
                                dates.min()
                                .strftime("%d %b %Y")
                            )

                            end_date = (
                                dates.max()
                                .strftime("%d %b %Y")
                            )

                            st.caption(
                                f"📅 {start_date} → "
                                f"{end_date}"
                            )

                    except Exception:
                        pass

            else:

                # Data_loaded may briefly be True while the
                # dataframe is unavailable. Do not crash.

                st.session_state.data_loaded = False


# ============================================================
# HERO
# ============================================================

def render_hero():
    """Render application hero."""

    st.markdown(
        '<div class="hero-container"><div class="hero-title">🛡️ SpendShield AI</div><div class="hero-subtitle">Your money has a problem. We found it.</div></div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<hr class="custom-divider">',
        unsafe_allow_html=True,
    )

# ============================================================
# LANDING PAGE
# ============================================================

def render_landing_page():
    """Render page before data is loaded."""

    st.markdown(
        """
        <div style="
            text-align:center;
            padding:2rem 1rem;
        ">

        <div style="font-size:4rem;">
            🛡️
        </div>

        <h2>
            Take control of your money.
        </h2>

        <p style="
            opacity:0.7;
            font-size:1.05rem;
        ">
            Upload your expense history and let SpendShield AI
            uncover your biggest money leaks.
        </p>

        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("---")

    col1, col2, col3 = st.columns(3)

    with col1:

        st.markdown("### 📊 Understand")

        st.caption(
            "Visualize spending by category, "
            "transaction type and time."
        )

    with col2:

        st.markdown("### 🤖 Diagnose")

        st.caption(
            "Use AI to discover spending patterns "
            "and money leaks."
        )

    with col3:

        st.markdown("### 🛡️ Recover")

        st.caption(
            "Get a personalized action plan "
            "based on your spending."
        )

    st.markdown("---")

    st.info(
        "👈 Upload a CSV from the sidebar or "
        "load the demo dataset."
    )

    st.markdown(
        "### 📋 Required CSV Format"
    )

    sample = pd.DataFrame(
        {
            "date": ["2026-01-01"],
            "description": ["Groceries"],
            "category": ["Food"],
            "amount": [2500],
            "type": ["Essential"]
        }
    )

    st.dataframe(
        sample,
        use_container_width=True,
        hide_index=True
    )

    st.caption(
        "Required columns: date, description, "
        "category, amount, type"
    )


# ============================================================
# DASHBOARD
# ============================================================

def render_dashboard(
    df,
    metrics
):
    """Render dashboard."""

    st.markdown(
        '<div class="section-title">'
        '📊 Financial Dashboard'
        '</div>',
        unsafe_allow_html=True
    )

    # --------------------------------------------------------
    # KPI ROW
    # --------------------------------------------------------

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "💰 Total Spending",
            format_currency(
                metrics["total_spending"]
            ),
            delta=(
                f"{format_currency(metrics['avg_monthly'])}"
                " avg/month"
            )
        )

    with col2:

        st.metric(
            "🎯 Discretionary",
            format_currency(
                metrics["discretionary"]
            ),
            delta=(
                f"{metrics['discretionary_pct']:.1f}%"
            ),
            delta_color="inverse"
        )

    with col3:

        st.metric(
            "💎 Potential Savings",
            format_currency(
                metrics["potential_savings"]
            ),
            delta=(
                f"{format_currency(metrics['potential_savings'] * 12)}"
                " /year"
            )
        )

    with col4:

        score = get_financial_health_score(
            metrics
        )

        st.metric(
            "🛡️ Spending Health",
            f"{score}/100",
            delta=health_label(score),
            delta_color="off"
        )

    st.markdown("---")

    # --------------------------------------------------------
    # CHARTS
    # --------------------------------------------------------

    col1, col2 = st.columns(2)

    with col1:

        st.subheader(
            "📊 Spending by Category"
        )

        try:

            fig = charts.create_category_chart(
                df
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        except Exception as e:

            st.error(
                f"Could not create category chart: {str(e)}"
            )

    with col2:

        st.subheader(
            "📈 Essential vs Discretionary"
        )

        try:

            fig = (
                charts
                .create_essential_vs_discretionary(
                    df
                )
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        except Exception as e:

            st.error(
                f"Could not create spending chart: {str(e)}"
            )

    col3, col4 = st.columns(2)

    with col3:

        st.subheader(
            "📉 Top Spending Categories"
        )

        try:

            fig = (
                charts
                .create_top_categories_chart(
                    df
                )
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        except Exception as e:

            st.error(
                f"Could not create category chart: {str(e)}"
            )

    with col4:

        st.subheader(
            "📅 Spending Trend"
        )

        try:

            fig = charts.create_trend_chart(
                df.copy()
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        except Exception as e:

            st.error(
                f"Could not create trend chart: {str(e)}"
            )

    # --------------------------------------------------------
    # AI ANALYSIS
    # --------------------------------------------------------

    st.markdown("---")

    st.markdown(
        '<div class="section-title">'
        '🤖 AI Financial Diagnosis'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="ai-card">

        <div class="ai-card-title">
        Find your biggest money leaks.
        </div>

        <div class="ai-card-text">
        SpendShield AI will analyze your spending,
        roast your worst habits, and create a
        personalized recovery plan.
        </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    if st.button(
        "🔍 Analyze My Spending",
        use_container_width=True,
        key="analyze_spending"
    ):

        with st.spinner(
            "🧠 AI is analyzing your spending..."
        ):

            try:

                result = (
                    gemini_service
                    .analyze_spending(df)
                )

                if result:

                    st.session_state.roast_result = (
                        result.get("roast")
                    )

                    st.session_state.recovery_plan = (
                        result.get(
                            "recovery_plan"
                        )
                    )

                    st.session_state.analysis_done = True

                    st.session_state.analysis_version = (
                        st.session_state.data_version
                    )

                    st.session_state.analysis_timestamp = (
                        datetime.now()
                    )

                    st.success(
                        "✅ Analysis complete!"
                    )

                    st.rerun()

                else:

                    st.error(
                        "❌ Gemini could not analyze "
                        "your spending."
                    )

            except Exception as e:

                st.error(
                    f"Analysis failed: {str(e)}"
                )

    # --------------------------------------------------------
    # AI RESULTS
    # --------------------------------------------------------

    if st.session_state.analysis_done:

        st.markdown("---")

        with st.expander(
            "🔥 Brutal Roast",
            expanded=True
        ):

            roast = (
                st.session_state.roast_result
            )

            if roast:

                st.markdown(
                    roast
                )

            else:

                st.info(
                    "No roast was returned."
                )

        with st.expander(
            "📋 Recovery Plan",
            expanded=True
        ):

            plan = (
                st.session_state.recovery_plan
            )

            if isinstance(plan, dict):

                st.markdown(
                    f"### "
                    f"{plan.get('summary', 'Recovery Plan')}"
                )

                col1, col2 = st.columns(2)

                with col1:

                    st.metric(
                        "Monthly Savings",
                        format_currency(
                            plan.get(
                                "monthly_savings",
                                0
                            )
                        )
                    )

                with col2:

                    st.metric(
                        "Annual Savings",
                        format_currency(
                            plan.get(
                                "annual_savings",
                                0
                            )
                        )
                    )

                st.markdown(
                    "#### 🔥 Top Money Leaks"
                )

                for leak in plan.get(
                    "top_leaks",
                    []
                ):

                    st.markdown(
                        f"- {leak}"
                    )

                st.markdown(
                    "#### ✂️ Recommended Cuts"
                )

                for cut in plan.get(
                    "recommended_cuts",
                    []
                ):

                    st.markdown(
                        f"- {cut}"
                    )

                st.markdown(
                    "#### ✅ Priority Actions"
                )

                for action in plan.get(
                    "priority_actions",
                    []
                ):

                    st.markdown(
                        f"- {action}"
                    )

                challenge = plan.get(
                    "weekly_challenge"
                )

                if challenge:

                    st.markdown(
                        f"**Weekly Challenge:** "
                        f"{challenge}"
                    )

            else:

                st.markdown(
                    str(plan)
                )


# ============================================================
# DATA EDITOR
# ============================================================

def render_data_editor(df):
    """Render editable expense table."""

    st.markdown(
        '<div class="section-title">'
        '✏️ Data Editor'
        '</div>',
        unsafe_allow_html=True
    )

    st.info(
        "Edit your expense data below. "
        "Changes are stored in your current session."
    )

    edited_df = st.data_editor(
        df,
        use_container_width=True,
        num_rows="dynamic",
        hide_index=True,
        key="expense_data_editor"
    )

    if edited_df is not None:

        if not edited_df.equals(df):

            edited_df = edited_df.copy()

            update_data(
                edited_df
            )

            st.success(
                "✅ Expense data updated."
            )

            st.rerun()

    st.markdown("---")

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "Transactions",
            f"{len(edited_df):,}"
        )

    with col2:

        total = pd.to_numeric(
            edited_df["amount"],
            errors="coerce"
        ).sum()

        st.metric(
            "Total Spending",
            format_currency(total)
        )

    with col3:

        average = pd.to_numeric(
            edited_df["amount"],
            errors="coerce"
        ).mean()

        st.metric(
            "Average Transaction",
            format_currency(average)
        )


# ============================================================
# RECEIPT SCANNER
# ============================================================

def render_receipt_scanner():
    """Render receipt scanner."""

    st.markdown(
        '<div class="section-title">'
        '📸 Receipt Scanner'
        '</div>',
        unsafe_allow_html=True
    )

    st.info(
        "Upload or photograph a receipt and Gemini "
        "will extract the expense information."
    )

    from services import receipt_service

    input_method = st.radio(
        "Choose input method",
        [
            "Upload Image",
            "Take Photo"
        ],
        horizontal=True
    )

    image_data = None

    if input_method == "Upload Image":

        image_data = st.file_uploader(
            "Upload receipt",
            type=[
                "jpg",
                "jpeg",
                "png",
                "webp"
            ],
            key="receipt_upload"
        )

    else:

        image_data = st.camera_input(
            "Take a photo of your receipt"
        )

    if image_data is not None:

        st.image(
            image_data,
            caption="Receipt",
            use_container_width=True
        )

        if st.button(
            "🔍 Extract Receipt Data",
            use_container_width=True,
            key="extract_receipt"
        ):

            with st.spinner(
                "🧠 Gemini is reading your receipt..."
            ):

                try:

                    extracted = (
                        receipt_service
                        .extract_receipt_data(
                            image_data
                        )
                    )

                    if extracted:

                        st.session_state.receipt_data = (
                            extracted
                        )

                        st.success(
                            "✅ Receipt data extracted!"
                        )

                        st.rerun()

                    else:

                        st.error(
                            "❌ Gemini could not extract "
                            "receipt data."
                        )

                except Exception as e:

                    st.error(
                        f"Receipt extraction failed: {str(e)}"
                    )

    # --------------------------------------------------------
    # DISPLAY RECEIPT DATA
    # --------------------------------------------------------

    data = st.session_state.get(
        "receipt_data"
    )

    if data:

        st.markdown("---")

        st.subheader(
            "📋 Extracted Receipt Data"
        )

        st.write(
            f"**Merchant:** "
            f"{data.get('merchant') or 'N/A'}"
        )

        st.write(
            f"**Date:** "
            f"{data.get('date') or 'N/A'}"
        )

        amount = data.get(
            "amount"
        )

        if amount is not None:

            try:

                st.write(
                    f"**Amount:** "
                    f"₹{float(amount):,.2f}"
                )

            except Exception:

                st.write(
                    f"**Amount:** {amount}"
                )

        else:

            st.write(
                "**Amount:** N/A"
            )

        st.write(
            f"**Category:** "
            f"{data.get('category') or 'Other'}"
        )

        items = data.get(
            "items",
            []
        )

        if items:

            st.markdown(
                "**Items:**"
            )

            for item in items:

                st.markdown(
                    f"- {item}"
                )

        col1, col2 = st.columns(2)

        with col1:

            if st.button(
                "✅ Confirm & Add Expense",
                use_container_width=True,
                key="confirm_receipt"
            ):

                try:

                    amount = float(
                        data.get(
                            "amount",
                            0
                        )
                    )

                except (
                    ValueError,
                    TypeError
                ):

                    amount = 0

                if amount <= 0:

                    st.error(
                        "Invalid receipt amount."
                    )

                else:

                    current_df = (
                        st.session_state
                        .df_cleaned
                    )

                    new_row = pd.DataFrame(
                        [
                            {
                                "date": data.get(
                                    "date",
                                    pd.Timestamp.now().date()
                                ),
                                "description": data.get(
                                    "merchant",
                                    "Receipt"
                                ),
                                "category": data.get(
                                    "category",
                                    "Other"
                                ),
                                "amount": amount,
                                "type": "Discretionary"
                            }
                        ]
                    )

                    updated_df = pd.concat(
                        [
                            current_df,
                            new_row
                        ],
                        ignore_index=True
                    )

                    update_data(
                        updated_df
                    )

                    st.session_state.receipt_data = (
                        None
                    )

                    st.success(
                        "✅ Expense added to SpendShield."
                    )

                    st.rerun()

        with col2:

            if st.button(
                "❌ Discard",
                use_container_width=True,
                key="discard_receipt"
            ):

                st.session_state.receipt_data = (
                    None
                )

                st.rerun()


# ============================================================
# MAIN APPLICATION
# ============================================================

def main():
    """Application controller."""

    render_sidebar()

    render_hero()

    # --------------------------------------------------------
    # NO DATA
    # --------------------------------------------------------

    if not st.session_state.data_loaded:

        render_landing_page()

        return

    # --------------------------------------------------------
    # VALIDATE DATA
    # --------------------------------------------------------

    df = st.session_state.get(
        "df_cleaned"
    )

    if (
        df is None
        or not isinstance(
            df,
            pd.DataFrame
        )
        or df.empty
    ):

        st.session_state.data_loaded = False

        st.warning(
            "Your dataset does not contain any "
            "valid transactions."
        )

        render_landing_page()

        return

    # --------------------------------------------------------
    # DATA VERSION
    # --------------------------------------------------------

    if st.session_state.data_version is None:

        st.session_state.data_version = (
            dataframe_signature(df)
        )

    # --------------------------------------------------------
    # NAVIGATION
    # --------------------------------------------------------

    section = st.session_state.nav_section

    if section == "Dashboard":

        metrics = (
            calculations.calculate_metrics(
                df
            )
        )

        render_dashboard(
            df,
            metrics
        )

    elif section == "Data Editor":

        render_data_editor(
            df
        )

    elif section == "Budget Simulator":

        st.markdown(
            '<div class="section-title">'
            '🎯 Budget Simulator'
            '</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            '<div class="section-description">'
            'Experiment with spending reductions and '
            'see their potential impact.'
            '</div>',
            unsafe_allow_html=True
        )

        budget_simulator.render_simulator(
            df
        )

    elif section == "Receipt Scanner":

        render_receipt_scanner()

    else:

        st.session_state.nav_section = (
            "Dashboard"
        )

        st.rerun()


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    main()