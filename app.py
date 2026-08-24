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

/* -------------------- GLOBAL -------------------- */

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


/* -------------------- HERO -------------------- */

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


/* -------------------- SECTION HEADERS -------------------- */

.section-title {
    font-size: 1.5rem;
    font-weight: 700;
    margin-top: 1rem;
}

.section-description {
    opacity: 0.7;
    margin-bottom: 1rem;
}


/* -------------------- DIVIDER -------------------- */

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


/* -------------------- AI CARD -------------------- */

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

.ai-card-title {
    font-size: 1.25rem;
    font-weight: 700;
}

.ai-card-text {
    opacity: 0.75;
}


/* -------------------- HEALTH SCORE -------------------- */

.health-score {
    text-align: center;
    padding: 1.5rem;
    border-radius: 18px;
    border: 1px solid rgba(128, 128, 128, 0.15);
    background: rgba(128, 128, 128, 0.04);
}

.health-score-number {
    font-size: 3rem;
    font-weight: 800;
}

.health-score-label {
    font-size: 1rem;
    opacity: 0.7;
}


/* -------------------- INSIGHT CARDS -------------------- */

.insight-card {
    padding: 1rem 1.2rem;
    border-radius: 12px;
    border: 1px solid rgba(128, 128, 128, 0.15);
    background: rgba(128, 128, 128, 0.04);
    margin-bottom: 0.7rem;
}

.insight-title {
    font-weight: 700;
    margin-bottom: 0.2rem;
}

.insight-text {
    opacity: 0.75;
}


/* -------------------- BUTTONS -------------------- */

.stButton > button {
    border-radius: 10px;
    font-weight: 600;
    transition: all 0.2s ease;
}

.stButton > button:hover {
    transform: translateY(-1px);
}


/* -------------------- SIDEBAR -------------------- */

.sidebar-brand {
    font-size: 1.35rem;
    font-weight: 800;
}

.sidebar-caption {
    font-size: 0.8rem;
    opacity: 0.6;
}


/* -------------------- STATUS -------------------- */

.status-pill {
    display: inline-block;
    padding: 0.25rem 0.7rem;
    border-radius: 999px;
    font-size: 0.75rem;
    font-weight: 600;
    background: rgba(46, 204, 113, 0.12);
}


/* -------------------- MOBILE -------------------- */

@media (max-width: 768px) {
    .main {
        padding: 0.5rem;
    }

    .block-container {
        padding-left: 0.75rem;
        padding-right: 0.75rem;
    }
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
        "data_version": None,
        "analysis_version": None,
        "analysis_timestamp": None,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


init_session_state()


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def dataframe_signature(df):
    """
    Create a lightweight signature for the current dataframe.

    Used to determine whether the data has changed since the
    previous AI analysis.
    """

    if df is None or df.empty:
        return None

    try:
        raw = pd.util.hash_pandas_object(
            df,
            index=True
        ).values.tobytes()

        return hashlib.md5(raw).hexdigest()

    except Exception:
        return str(len(df))


def invalidate_analysis():
    """Clear AI results because underlying expense data changed."""

    st.session_state.analysis_done = False
    st.session_state.roast_result = None
    st.session_state.recovery_plan = None
    st.session_state.analysis_version = None
    st.session_state.analysis_timestamp = None


def update_data(df):
    """Update dataframe and invalidate stale AI analysis."""

    st.session_state.df_cleaned = df.copy()
    st.session_state.data_version = dataframe_signature(df)

    invalidate_analysis()


def get_financial_health_score(metrics):
    """
    Calculate an approximate expense-health score.

    Important:
    This is NOT a complete financial health score because
    income, debt, investments and savings balances are unknown.

    The score is based only on spending behavior.
    """

    discretionary_pct = metrics.get("discretionary_pct", 0)

    score = 100

    # Penalize high discretionary spending.
    if discretionary_pct > 60:
        score -= 35
    elif discretionary_pct > 50:
        score -= 25
    elif discretionary_pct > 40:
        score -= 15
    elif discretionary_pct > 30:
        score -= 8

    # Reward lower discretionary spending.
    elif discretionary_pct <= 20:
        score += 0

    # Keep within range.
    score = max(0, min(100, score))

    return score


def health_label(score):
    """Return a human-readable health label."""

    if score >= 85:
        return "Excellent"
    if score >= 70:
        return "Healthy"
    if score >= 50:
        return "Needs Attention"

    return "High Risk"


def format_currency(value):
    """Format Indian Rupee values consistently."""

    try:
        return f"₹{float(value):,.0f}"
    except (TypeError, ValueError):
        return "₹0"


# ============================================================
# SIDEBAR
# ============================================================

def render_sidebar():
    """Render the application sidebar."""

    with st.sidebar:

        st.markdown(
            '<div class="sidebar-brand">🛡️ SpendShield AI</div>',
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
            )
        )

        if uploaded_file is not None:

            # Detect a new uploaded file.
            file_id = f"{uploaded_file.name}_{uploaded_file.size}"

            if st.session_state.get("uploaded_file_id") != file_id:

                with st.spinner("🔄 Processing your expenses..."):

                    df = expense_service.load_and_validate_csv(
                        uploaded_file
                    )

                    if df is not None and not df.empty:

                        cleaned_df = expense_service.clean_data(df)

                        if cleaned_df.empty:
                            st.error(
                                "The file contains no valid expense "
                                "transactions after cleaning."
                            )
                        else:
                            st.session_state.df_raw = df

                            update_data(cleaned_df)

                            st.session_state.data_loaded = True
                            st.session_state.uploaded_file_id = file_id

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
            use_container_width=True
        ):

            demo_df = expense_service.get_sample_data()

            update_data(demo_df)

            st.session_state.df_raw = demo_df.copy()
            st.session_state.data_loaded = True
            st.session_state.uploaded_file_id = "demo"

            st.rerun()

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

            if st.button(
                label,
                use_container_width=True,
                type=(
                    "primary"
                    if st.session_state.nav_section == option
                    else "secondary"
                )
            ):
                st.session_state.nav_section = option
                st.rerun()

        # ----------------------------------------------------
        # DATA SUMMARY
        # ----------------------------------------------------

        if st.session_state.data_loaded:

            st.markdown("---")
            st.markdown("#### 📊 Dataset")

            df = st.session_state.df_cleaned

            st.metric(
                "Total Spending",
                format_currency(df["amount"].sum())
            )

            st.metric(
                "Transactions",
                f"{len(df):,}"
            )

            if "date" in df.columns and not df.empty:

                start_date = pd.to_datetime(
                    df["date"]
                ).min().strftime("%d %b %Y")

                end_date = pd.to_datetime(
                    df["date"]
                ).max().strftime("%d %b %Y")

                st.caption(
                    f"📅 {start_date} → {end_date}"
                )

            # ------------------------------------------------
            # DOWNLOAD
            # ------------------------------------------------

            st.markdown("---")

            csv_data = df.to_csv(index=False).encode("utf-8")

            st.download_button(
                "⬇️ Download Cleaned CSV",
                data=csv_data,
                file_name="spendshield_cleaned_expenses.csv",
                mime="text/csv",
                use_container_width=True
            )


# ============================================================
# HERO
# ============================================================

def render_hero():
    """Render application hero section."""

    st.markdown(
        """
        <div class="hero-container">
            <h1 class="hero-title">🛡️ SpendShield AI</h1>
            <p class="hero-subtitle">
                Your money has a problem. We found it.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        '<hr class="custom-divider">',
        unsafe_allow_html=True
    )


# ============================================================
# DASHBOARD
# ============================================================

def render_dashboard(df, metrics):
    """Render the main financial intelligence dashboard."""

    # --------------------------------------------------------
    # HEADER
    # --------------------------------------------------------

    st.markdown(
        '<div class="section-title">Financial Command Center</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-description">'
        'Understand where your money goes, identify leaks, '
        'and turn spending data into an actionable plan.'
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
            format_currency(metrics["total_spending"]),
            help="Total valid expenses in the uploaded dataset."
        )

    with col2:

        st.metric(
            "🎯 Discretionary",
            format_currency(metrics["discretionary"]),
            delta=f"{metrics['discretionary_pct']:.1f}% of spending",
            help=(
                "Expenses classified as discretionary. "
                "These are usually the easiest expenses to optimize."
            )
        )

    with col3:

        st.metric(
            "💎 Savings Opportunity",
            format_currency(metrics["potential_savings"]),
            delta=f"{metrics['potential_savings'] * 12:,.0f}/yr",
            delta_color="normal",
            help=(
                "Estimated opportunity if approximately 30% "
                "of discretionary spending is reduced."
            )
        )

    with col4:

        st.metric(
            "📅 Daily Average",
            format_currency(metrics["avg_daily"]),
            help="Average spending per day across the dataset."
        )

    # --------------------------------------------------------
    # HEALTH + SUMMARY
    # --------------------------------------------------------

    st.markdown(
        '<hr class="custom-divider">',
        unsafe_allow_html=True
    )

    health_score = get_financial_health_score(metrics)
    label = health_label(health_score)

    col1, col2, col3 = st.columns([1, 2, 2])

    with col1:

        st.markdown(
            f"""
            <div class="health-score">
                <div class="health-score-number">
                    {health_score}/100
                </div>
                <div class="health-score-label">
                    Spending Health<br>
                    <strong>{label}</strong>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:

        st.markdown("### 💡 Quick Diagnosis")

        if metrics["discretionary_pct"] > 40:

            st.warning(
                f"Your discretionary spending is "
                f"{metrics['discretionary_pct']:.1f}% of total spending. "
                "This is your biggest optimization opportunity."
            )

        elif metrics["discretionary_pct"] > 25:

            st.info(
                f"{metrics['discretionary_pct']:.1f}% of your spending "
                "is discretionary. There may be room for meaningful "
                "optimization."
            )

        else:

            st.success(
                f"Only {metrics['discretionary_pct']:.1f}% of your "
                "spending is discretionary. Your expense mix looks "
                "relatively controlled."
            )

    with col3:

        st.markdown("### 🎯 Optimization Target")

        target = metrics["potential_savings"]

        st.metric(
            "Potential Monthly Reduction",
            format_currency(target)
        )

        st.caption(
            "Illustrative target based on reducing ~30% "
            "of discretionary expenses."
        )

    # --------------------------------------------------------
    # CHARTS
    # --------------------------------------------------------

    st.markdown(
        '<hr class="custom-divider">',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-title">Spending Intelligence</div>',
        unsafe_allow_html=True
    )

    col1, col2 = st.columns(2)

    with col1:

        st.subheader("📊 Spending by Category")

        fig = charts.create_category_chart(df)

        st.plotly_chart(
            fig,
            use_container_width=True,
            key="category_chart"
        )

    with col2:

        st.subheader("⚖️ Essential vs Discretionary")

        fig = charts.create_essential_vs_discretionary(df)

        st.plotly_chart(
            fig,
            use_container_width=True,
            key="essential_chart"
        )

    col1, col2 = st.columns(2)

    with col1:

        st.subheader("🔥 Top Spending Categories")

        fig = charts.create_top_categories_chart(df)

        st.plotly_chart(
            fig,
            use_container_width=True,
            key="top_categories_chart"
        )

    with col2:

        st.subheader("📈 Spending Trend")

        fig = charts.create_trend_chart(df)

        st.plotly_chart(
            fig,
            use_container_width=True,
            key="trend_chart"
        )

    # --------------------------------------------------------
    # AI ANALYSIS
    # --------------------------------------------------------

    render_ai_analysis(df)


# ============================================================
# AI ANALYSIS
# ============================================================

def render_ai_analysis(df):
    """Render AI financial diagnosis and recovery plan."""

    st.markdown(
        '<hr class="custom-divider">',
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="ai-card">
            <div class="ai-card-title">
                🤖 AI Financial Diagnosis
            </div>
            <div class="ai-card-text">
                SpendShield analyzes your actual transactions to
                identify money leaks, recurring expenses and
                opportunities for improvement.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    current_version = dataframe_signature(df)

    # Detect if displayed analysis is stale.
    if (
        st.session_state.analysis_done
        and st.session_state.analysis_version != current_version
    ):
        invalidate_analysis()

    col1, col2 = st.columns([3, 1])

    with col1:

        if st.session_state.analysis_done:

            timestamp = st.session_state.analysis_timestamp

            if timestamp:

                st.caption(
                    f"Analysis generated on "
                    f"{timestamp.strftime('%d %b %Y at %I:%M %p')}"
                )

        else:

            st.markdown(
                "Get a brutally honest diagnosis and a "
                "personalized recovery strategy."
            )

    with col2:

        button_text = (
            "🔄 Re-analyze"
            if st.session_state.analysis_done
            else "🔍 Analyze My Spending"
        )

        analyze_button = st.button(
            button_text,
            use_container_width=True,
            type="primary"
        )

    if analyze_button:

        with st.spinner(
            "🧠 AI is studying your spending patterns..."
        ):

            try:

                result = gemini_service.analyze_spending(df)

                if result:

                    st.session_state.roast_result = (
                        result.get("roast")
                    )

                    st.session_state.recovery_plan = (
                        result.get("recovery_plan")
                    )

                    st.session_state.analysis_done = True
                    st.session_state.analysis_version = (
                        current_version
                    )

                    st.session_state.analysis_timestamp = (
                        datetime.now()
                    )

                    st.success(
                        "✅ Financial diagnosis complete."
                    )

                    st.rerun()

                else:

                    st.error(
                        "The AI analysis could not be completed. "
                        "Please check your Gemini API configuration."
                    )

            except Exception as e:

                st.error(
                    f"Analysis failed: {str(e)}"
                )

    # --------------------------------------------------------
    # DISPLAY RESULTS
    # --------------------------------------------------------

    if not st.session_state.analysis_done:
        return

    roast = st.session_state.roast_result
    plan = st.session_state.recovery_plan

    # --------------------------------------------------------
    # ROAST
    # --------------------------------------------------------

    if roast:

        with st.expander(
            "🔥 Your Financial Roast",
            expanded=True
        ):

            st.markdown(roast)

    # --------------------------------------------------------
    # RECOVERY PLAN
    # --------------------------------------------------------

    if plan:

        with st.expander(
            "🛡️ Your Recovery Plan",
            expanded=True
        ):

            if isinstance(plan, dict):

                summary = plan.get(
                    "summary",
                    "Your personalized recovery strategy."
                )

                st.markdown(
                    f"### {summary}"
                )

                # Savings metrics
                col1, col2, col3 = st.columns(3)

                monthly_savings = plan.get(
                    "monthly_savings",
                    0
                )

                annual_savings = plan.get(
                    "annual_savings",
                    0
                )

                with col1:

                    st.metric(
                        "💰 Monthly Opportunity",
                        format_currency(monthly_savings)
                    )

                with col2:

                    st.metric(
                        "📈 Annual Opportunity",
                        format_currency(annual_savings)
                    )

                with col3:

                    if annual_savings:

                        st.metric(
                            "🚀 12-Month Impact",
                            format_currency(annual_savings)
                        )

                    else:

                        st.metric(
                            "🚀 Priority",
                            "Start Now"
                        )

                # Money leaks
                top_leaks = plan.get(
                    "top_leaks",
                    []
                )

                if top_leaks:

                    st.markdown("#### 🔥 Biggest Money Leaks")

                    for index, leak in enumerate(
                        top_leaks,
                        start=1
                    ):

                        st.markdown(
                            f"**{index}.** {leak}"
                        )

                # Recommended cuts
                cuts = plan.get(
                    "recommended_cuts",
                    []
                )

                if cuts:

                    st.markdown(
                        "#### ✂️ Recommended Cuts"
                    )

                    for cut in cuts:

                        st.markdown(
                            f"- {cut}"
                        )

                # Priority actions
                actions = plan.get(
                    "priority_actions",
                    []
                )

                if actions:

                    st.markdown(
                        "#### ✅ Priority Actions"
                    )

                    for index, action in enumerate(
                        actions,
                        start=1
                    ):

                        st.markdown(
                            f"**{index}.** {action}"
                        )

                # Weekly challenge
                challenge = plan.get(
                    "weekly_challenge"
                )

                if challenge:

                    st.markdown(
                        "#### 🏆 7-Day Challenge"
                    )

                    st.info(challenge)

            else:

                st.markdown(str(plan))


# ============================================================
# DATA EDITOR
# ============================================================

def render_data_editor(df):
    """Render editable expense dataset."""

    st.markdown(
        '<div class="section-title">'
        '✏️ Expense Data Editor'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-description">'
        'Correct transactions, categorize expenses and '
        'immediately see the effect on your financial analysis.'
        '</div>',
        unsafe_allow_html=True
    )

    if df.empty:

        st.warning(
            "There are no transactions to edit."
        )

        return

    edited_df = st.data_editor(
        df,
        use_container_width=True,
        num_rows="dynamic",
        hide_index=True,
        key="expense_data_editor",
        column_config={
            "date": st.column_config.DateColumn(
                "Date",
                format="DD MMM YYYY"
            ),

            "description": st.column_config.TextColumn(
                "Description",
                required=True
            ),

            "category": st.column_config.SelectboxColumn(
                "Category",
                options=sorted(
                    df["category"]
                    .dropna()
                    .astype(str)
                    .unique()
                    .tolist()
                )
            ),

            "amount": st.column_config.NumberColumn(
                "Amount",
                format="₹%.2f",
                min_value=0
            ),

            "type": st.column_config.SelectboxColumn(
                "Type",
                options=[
                    "Essential",
                    "Discretionary"
                ]
            )
        }
    )

    if edited_df is None:
        return

    # Normalize edited dataframe.
    edited_df = edited_df.copy()

    if "amount" in edited_df.columns:

        edited_df["amount"] = pd.to_numeric(
            edited_df["amount"],
            errors="coerce"
        )

    # Detect modifications.
    if not edited_df.equals(df):

        edited_df = edited_df.dropna(
            subset=["amount"]
        )

        edited_df = edited_df[
            edited_df["amount"] > 0
        ]

        update_data(edited_df)

        st.success(
            "✅ Changes saved. AI analysis has been refreshed "
            "to reflect the updated data."
        )

    # --------------------------------------------------------
    # DATA STATISTICS
    # --------------------------------------------------------

    st.markdown("---")

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "Transactions",
            f"{len(edited_df):,}"
        )

    with col2:

        st.metric(
            "Total Spending",
            format_currency(
                edited_df["amount"].sum()
            )
        )

    with col3:

        st.metric(
            "Average Transaction",
            f"₹{edited_df['amount'].mean():,.0f}"
            if not edited_df.empty
            else "₹0"
        )

    with col4:

        if not edited_df.empty:

            largest = edited_df["amount"].max()

        else:

            largest = 0

        st.metric(
            "Largest Expense",
            format_currency(largest)
        )


# ============================================================
# RECEIPT SCANNER
# ============================================================

def render_receipt_scanner():
    """Render AI-powered receipt scanner."""

    st.markdown(
        '<div class="section-title">'
        '📸 AI Receipt Scanner'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-description">'
        'Upload a receipt and let AI extract the transaction '
        'details automatically.'
        '</div>',
        unsafe_allow_html=True
    )

    try:

        from services import receipt_service

    except ImportError:

        st.error(
            "Receipt scanner service is not available."
        )

        return

    input_method = st.radio(
        "Receipt source",
        [
            "📁 Upload Image",
            "📷 Take Photo"
        ],
        horizontal=True
    )

    image_data = None

    if input_method == "📁 Upload Image":

        image_data = st.file_uploader(
            "Choose a receipt image",
            type=[
                "jpg",
                "jpeg",
                "png",
                "webp"
            ],
            help="Use a clear, well-lit receipt image."
        )

    else:

        image_data = st.camera_input(
            "Take a photo of your receipt"
        )

    if image_data is not None:

        st.image(
            image_data,
            caption="Receipt Preview",
            use_container_width=True
        )

        if st.button(
            "🔍 Extract Transaction",
            use_container_width=True,
            type="primary"
        ):

            with st.spinner(
                "🧠 AI is reading your receipt..."
            ):

                try:

                    extracted = (
                        receipt_service.extract_receipt_data(
                            image_data
                        )
                    )

                    if extracted:

                        st.session_state.receipt_data = (
                            extracted
                        )

                        st.success(
                            "✅ Receipt successfully processed."
                        )

                        st.rerun()

                    else:

                        st.error(
                            "Could not extract useful data "
                            "from this receipt."
                        )

                except Exception as e:

                    st.error(
                        f"Receipt extraction failed: {str(e)}"
                    )

    # --------------------------------------------------------
    # EXTRACTED DATA
    # --------------------------------------------------------

    data = st.session_state.receipt_data

    if not data:
        return

    st.markdown("---")

    st.subheader(
        "📋 Extracted Transaction"
    )

    # Handle raw text fallback.
    if "raw_text" in data and not data.get("merchant"):

        st.warning(
            "The AI could not confidently structure "
            "the receipt."
        )

        st.markdown(
            data.get("raw_text", "")
        )

        if st.button(
            "❌ Discard",
            use_container_width=True
        ):

            st.session_state.receipt_data = None
            st.rerun()

        return

    col1, col2 = st.columns(2)

    with col1:

        merchant = st.text_input(
            "Merchant",
            value=str(
                data.get(
                    "merchant",
                    ""
                ) or ""
            )
        )

        date_value = st.text_input(
            "Date",
            value=str(
                data.get(
                    "date",
                    ""
                ) or ""
            )
        )

        category = st.selectbox(
            "Category",
            [
                "Food",
                "Transport",
                "Shopping",
                "Entertainment",
                "Utilities",
                "Health",
                "Housing",
                "Dining",
                "Other"
            ],
            index=(
                [
                    "Food",
                    "Transport",
                    "Shopping",
                    "Entertainment",
                    "Utilities",
                    "Health",
                    "Housing",
                    "Dining",
                    "Other"
                ].index(
                    data.get(
                        "category",
                        "Other"
                    )
                )
                if data.get("category") in [
                    "Food",
                    "Transport",
                    "Shopping",
                    "Entertainment",
                    "Utilities",
                    "Health",
                    "Housing",
                    "Dining",
                    "Other"
                ]
                else 8
            )
        )

    with col2:

        try:

            amount_value = float(
                data.get(
                    "amount",
                    0
                ) or 0
            )

        except (TypeError, ValueError):

            amount_value = 0.0

        amount = st.number_input(
            "Amount (₹)",
            min_value=0.0,
            value=amount_value,
            step=1.0
        )

        expense_type = st.selectbox(
            "Expense Type",
            [
                "Discretionary",
                "Essential"
            ]
        )

    items = data.get(
        "items",
        []
    )

    if items:

        st.markdown("#### 🧾 Items")

        for item in items:

            st.markdown(
                f"- {item}"
            )

    # --------------------------------------------------------
    # CONFIRM / DISCARD
    # --------------------------------------------------------

    col1, col2 = st.columns(2)

    with col1:

        if st.button(
            "✅ Confirm & Add Expense",
            use_container_width=True,
            type="primary"
        ):

            if not merchant.strip():

                st.error(
                    "Please enter a merchant name."
                )

                return

            if amount <= 0:

                st.error(
                    "Amount must be greater than ₹0."
                )

                return

            try:

                parsed_date = pd.to_datetime(
                    date_value
                )

            except Exception:

                parsed_date = pd.Timestamp.now()

            current_df = st.session_state.df_cleaned

            new_row = pd.DataFrame(
                [{
                    "date": parsed_date,
                    "description": merchant.strip(),
                    "category": category,
                    "amount": amount,
                    "type": expense_type
                }]
            )

            updated_df = pd.concat(
                [
                    current_df,
                    new_row
                ],
                ignore_index=True
            )

            update_data(updated_df)

            st.session_state.receipt_data = None

            st.success(
                "✅ Expense added to SpendShield."
            )

            st.rerun()

    with col2:

        if st.button(
            "❌ Discard",
            use_container_width=True
        ):

            st.session_state.receipt_data = None
            st.rerun()


# ============================================================
# LANDING PAGE
# ============================================================

def render_landing_page():
    """Render the page shown before a dataset is loaded."""

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
            "Visualize spending by category, transaction type "
            "and time."
        )

    with col2:

        st.markdown("### 🤖 Diagnose")

        st.caption(
            "Use AI to discover recurring expenses and "
            "hidden spending patterns."
        )

    with col3:

        st.markdown("### 🛡️ Recover")

        st.caption(
            "Get a personalized action plan designed around "
            "your actual spending."
        )

    st.markdown("---")

    st.info(
        "👈 Upload a CSV from the sidebar or load the demo "
        "dataset to explore SpendShield AI."
    )

    st.markdown("### 📋 Required CSV Format")

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
        "Required columns: date, description, category, "
        "amount, type"
    )


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

    df = st.session_state.df_cleaned

    if df is None or df.empty:

        st.warning(
            "Your dataset does not contain any valid "
            "transactions."
        )

        return

    # Ensure data version exists.
    if st.session_state.data_version is None:

        st.session_state.data_version = (
            dataframe_signature(df)
        )

    # --------------------------------------------------------
    # NAVIGATION
    # --------------------------------------------------------

    section = st.session_state.nav_section

    if section == "Dashboard":

        metrics = calculations.calculate_metrics(df)

        render_dashboard(
            df,
            metrics
        )

    elif section == "Data Editor":

        render_data_editor(df)

    elif section == "Budget Simulator":

        st.markdown(
            '<div class="section-title">'
            '🎯 Budget Simulator'
            '</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            '<div class="section-description">'
            'Experiment with spending reductions and see '
            'their potential impact.'
            '</div>',
            unsafe_allow_html=True
        )

        budget_simulator.render_simulator(df)

    elif section == "Receipt Scanner":

        render_receipt_scanner()

    else:

        st.session_state.nav_section = "Dashboard"

        st.rerun()


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    main()