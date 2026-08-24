"""
SpendShield AI - Prompt Engineering

This module contains:
- Financial analysis context construction
- Combined AI analysis prompt
- Receipt extraction prompt

Design principle:

Python/Pandas = numerical source of truth
Gemini = reasoning, prioritization, explanation, and recommendations
"""


# =========================================================
# ANALYSIS CONTEXT
# =========================================================

def build_analysis_context(df):
    """
    Build a verified, compact financial context for Gemini.

    All numerical values are calculated in Python before being
    sent to the model. Gemini should interpret these values,
    not independently recalculate the user's finances.
    """

    from utils import calculations

    if df is None or df.empty:
        return {
            "total_spending": 0,
            "essential_spending": 0,
            "discretionary_spending": 0,
            "essential_pct": 0,
            "discretionary_pct": 0,
            "potential_savings": 0,
            "total_transactions": 0,
            "top_categories": [],
            "largest_transactions": [],
            "recurring_expenses": [],
            "anomalies": [],
            "date_range": "No data",
        }

    # -----------------------------------------------------
    # VERIFIED METRICS
    # -----------------------------------------------------

    metrics = calculations.calculate_metrics(df)

    # -----------------------------------------------------
    # CATEGORY ANALYSIS
    # -----------------------------------------------------

    category_stats = calculations.calculate_category_stats(df)

    top_categories = []

    if not category_stats.empty:
        for category, row in category_stats.head(7).iterrows():
            top_categories.append({
                "category": str(category),
                "total": round(
                    float(row["total"]),
                    2,
                ),
                "percentage": round(
                    float(row["percentage"]),
                    1,
                ),
                "transaction_count": int(
                    row["count"]
                ),
                "average_transaction": round(
                    float(row["average"]),
                    2,
                ),
            })

    # -----------------------------------------------------
    # LARGEST TRANSACTIONS
    # -----------------------------------------------------

    largest_transactions = []

    required_columns = [
        "description",
        "category",
        "amount",
    ]

    if all(
        column in df.columns
        for column in required_columns
    ):

        largest = df.nlargest(
            7,
            "amount",
        )

        for _, row in largest.iterrows():

            largest_transactions.append({
                "description": str(
                    row["description"]
                ),
                "category": str(
                    row["category"]
                ),
                "amount": round(
                    float(row["amount"]),
                    2,
                ),
            })

    # -----------------------------------------------------
    # RECURRING EXPENSES
    # -----------------------------------------------------

    recurring_expenses = []

    if "description" in df.columns:

        recurring = (
            df.groupby("description")
            .agg(
                transaction_count=(
                    "amount",
                    "count",
                ),
                total_spent=(
                    "amount",
                    "sum",
                ),
                average_amount=(
                    "amount",
                    "mean",
                ),
            )
        )

        recurring = recurring[
            recurring["transaction_count"] >= 2
        ]

        recurring = recurring.sort_values(
            "total_spent",
            ascending=False,
        ).head(7)

        for description, row in recurring.iterrows():

            recurring_expenses.append({
                "description": str(
                    description
                ),
                "transaction_count": int(
                    row["transaction_count"]
                ),
                "total_spent": round(
                    float(row["total_spent"]),
                    2,
                ),
                "average_amount": round(
                    float(row["average_amount"]),
                    2,
                ),
            })

    # -----------------------------------------------------
    # ANOMALIES
    # -----------------------------------------------------

    anomalies = []

    if (
        "is_anomaly" in df.columns
        and "amount" in df.columns
    ):

        anomaly_df = df[
            df["is_anomaly"] == True
        ].nlargest(
            5,
            "amount",
        )

        for _, row in anomaly_df.iterrows():

            anomalies.append({
                "description": str(
                    row["description"]
                ),
                "category": str(
                    row["category"]
                ),
                "amount": round(
                    float(row["amount"]),
                    2,
                ),
            })

    # -----------------------------------------------------
    # DATE RANGE
    # -----------------------------------------------------

    if "date" in df.columns:

        start_date = df["date"].min()
        end_date = df["date"].max()

        date_range = (
            f"{start_date.strftime('%d %b %Y')} "
            f"to "
            f"{end_date.strftime('%d %b %Y')}"
        )

    else:
        date_range = "Unknown"

    # -----------------------------------------------------
    # FINAL CONTEXT
    # -----------------------------------------------------

    return {
        # Verified financial metrics
        "total_spending": round(
            float(metrics["total_spending"]),
            2,
        ),
        "essential_spending": round(
            float(metrics["essential"]),
            2,
        ),
        "discretionary_spending": round(
            float(metrics["discretionary"]),
            2,
        ),
        "essential_pct": round(
            float(metrics["essential_pct"]),
            1,
        ),
        "discretionary_pct": round(
            float(metrics["discretionary_pct"]),
            1,
        ),
        "potential_savings": round(
            float(metrics["potential_savings"]),
            2,
        ),
        "average_monthly": round(
            float(metrics["avg_monthly"]),
            2,
        ),
        "average_daily": round(
            float(metrics["avg_daily"]),
            2,
        ),

        # Dataset information
        "total_transactions": len(df),
        "date_range": date_range,

        # Behavioral information
        "top_categories": top_categories,
        "largest_transactions": largest_transactions,
        "recurring_expenses": recurring_expenses,
        "anomalies": anomalies,
    }


# =========================================================
# COMBINED ANALYSIS PROMPT
# =========================================================

def get_combined_analysis_prompt(context):
    """
    Generate a single structured prompt for comprehensive
    financial analysis.

    Gemini returns both:
    - A humorous spending roast
    - A personalized recovery plan
    """

    return f"""
You are SpendShield AI, an intelligent personal-finance
coach that analyzes spending behavior.

Your job is NOT to blindly tell the user to spend less.

Your job is to:
1. Understand their spending pattern.
2. Identify the highest-impact money leaks.
3. Distinguish essential spending from discretionary spending.
4. Detect potentially recurring expenses.
5. Highlight unusual transactions when relevant.
6. Recommend realistic actions with measurable impact.
7. Explain the reasoning behind the recommendations.
8. Motivate the user without being judgmental.

============================================================
IMPORTANT DATA POLICY
============================================================

The financial numbers below were calculated by Python/Pandas.

THESE NUMBERS ARE THE SOURCE OF TRUTH.

Do NOT invent transactions.

Do NOT invent income.

Do NOT invent debts.

Do NOT assume the user's salary.

Do NOT assume financial obligations that are not present.

Do NOT change the supplied totals.

If a conclusion cannot be supported by the supplied data,
say that the information is unavailable.

You may perform simple reasoning using the supplied numbers,
but do not fabricate missing financial information.

============================================================
USER'S VERIFIED FINANCIAL DATA
============================================================

Total spending:
₹{context['total_spending']:,.2f}

Essential spending:
₹{context['essential_spending']:,.2f}
({context['essential_pct']:.1f}%)

Discretionary spending:
₹{context['discretionary_spending']:,.2f}
({context['discretionary_pct']:.1f}%)

Potential savings estimate:
₹{context['potential_savings']:,.2f}

Average daily spending:
₹{context['average_daily']:,.2f}

Estimated average monthly spending:
₹{context['average_monthly']:,.2f}

Number of transactions:
{context['total_transactions']}

Analysis period:
{context['date_range']}

============================================================
TOP SPENDING CATEGORIES
============================================================

{context['top_categories']}

============================================================
LARGEST TRANSACTIONS
============================================================

{context['largest_transactions']}

============================================================
POTENTIALLY RECURRING EXPENSES
============================================================

{context['recurring_expenses']}

============================================================
POTENTIAL ANOMALIES
============================================================

{context['anomalies']}

============================================================
ROAST
============================================================

Create a humorous financial roast.

Rules:

- Be witty, not abusive.
- Never insult the person's intelligence, appearance,
  character, background, or financial status.
- Use the actual numbers provided.
- Mention 1-3 concrete spending patterns.
- Use memorable analogies or financial jokes.
- Don't shame essential spending.
- Focus criticism on controllable spending behavior.
- Keep it concise: approximately 100-150 words.
- Finish the roast with a motivating transition toward
  improvement.

The roast should feel personalized rather than generic.

============================================================
RECOVERY STRATEGY
============================================================

Create a practical recovery plan.

Prioritize the largest controllable spending leaks first.

Do NOT recommend cutting essential expenses simply because
they are large.

For discretionary spending:

- Identify the highest-impact category.
- Suggest a realistic reduction percentage.
- Convert that percentage into an estimated rupee saving.
- Prioritize changes that can actually be implemented.
- Avoid extreme recommendations.

When recommending savings, make it clear that these are
ESTIMATES based only on the supplied expense data.

============================================================
BEHAVIORAL INSIGHT
============================================================

Identify the most interesting behavioral pattern visible
in the data.

Examples:

- repeated small purchases
- concentration in one category
- expensive recurring subscriptions
- unusually large discretionary purchases
- frequent dining/delivery
- shopping spikes
- weekend-heavy spending

Only mention a pattern if the data supports it.

============================================================
RESPONSE FORMAT
============================================================

Return ONLY valid JSON.

Use exactly this structure:

{{
    "roast": "100-150 word personalized financial roast",

    "financial_story": "2-4 sentence explanation of what the spending data says",

    "behavioral_insight": {{
        "title": "Short insight title",
        "explanation": "Evidence-based explanation",
        "evidence": [
            "Specific evidence from the dataset",
            "Another supporting observation"
        ]
    }},

    "top_leaks": [
        {{
            "category": "Category or expense",
            "amount": 0,
            "percentage_of_total": 0,
            "why_it_matters": "Why this deserves attention"
        }}
    ],

    "recommended_cuts": [
        {{
            "category": "Category",
            "current_spending": 0,
            "target_reduction_percent": 0,
            "estimated_monthly_saving": 0,
            "action": "Specific action"
        }}
    ],

    "recovery_plan": {{
        "summary": "Short personalized recovery strategy",

        "priority_actions": [
            {{
                "action": "Specific action",
                "reason": "Why it matters",
                "estimated_saving": 0
            }}
        ],

        "weekly_challenge": "A realistic 7-day challenge",

        "30_day_goal": "A measurable goal for the next 30 days"
    }},

    "estimated_savings": {{
        "monthly": 0,
        "yearly": 0,
        "assumption": "Explain how the estimate was derived"
    }}
}}

============================================================
FINAL QUALITY RULE
============================================================

Before returning the response, check:

1. Is every financial claim supported by the provided data?
2. Did you avoid inventing income?
3. Did you avoid inventing debts?
4. Did you avoid treating essential spending as waste?
5. Are recommendations specific?
6. Are savings estimates clearly labeled as estimates?
7. Is the JSON valid?
8. Did you use the actual user's numbers?

Return ONLY JSON.
"""


# =========================================================
# BACKWARD-COMPATIBILITY ROAST PROMPT
# =========================================================

def get_roast_prompt(context):
    """
    Legacy roast prompt.

    Kept so older components do not immediately break.
    New code should use get_combined_analysis_prompt().
    """

    return get_combined_analysis_prompt(
        context
    )


# =========================================================
# BACKWARD-COMPATIBILITY RECOVERY PROMPT
# =========================================================

def get_recovery_plan_prompt(context):
    """
    Legacy recovery-plan prompt.

    Kept for compatibility with older components.
    New code should use get_combined_analysis_prompt().
    """

    return get_combined_analysis_prompt(
        context
    )


# =========================================================
# RECEIPT EXTRACTION
# =========================================================

def get_receipt_extraction_prompt():
    """
    Generate a structured prompt for Gemini Vision receipt
    extraction.
    """

    return """
You are SpendShield AI's receipt extraction engine.

Your task is to read the provided receipt image and extract
ONLY information that is visibly supported by the image.

Do not guess.

Do not invent missing information.

============================================================
FIELDS TO EXTRACT
============================================================

merchant:
The store or merchant name.

date:
Purchase date in YYYY-MM-DD format.

amount:
Final total amount paid.

category:
Choose exactly one:

- Food
- Transport
- Shopping
- Entertainment
- Utilities
- Health
- Housing
- Dining
- Education
- Travel
- Other

items:
List the purchased items that can be clearly read.

============================================================
IMPORTANT RULES
============================================================

1. Prefer the final amount paid over subtotal or tax.
2. If multiple totals are visible, choose the final payable
   amount only when it is clear.
3. Never guess unreadable digits.
4. If the amount cannot be confidently determined, return null.
5. If the date cannot be confidently determined, return null.
6. If the merchant cannot be determined, return null.
7. Keep item names concise.
8. Do not include tax as a separate item.
9. Do not include payment-method information as an item.
10. Do not add information that is not visible.

============================================================
OUTPUT
============================================================

Return ONLY valid JSON.

Use exactly:

{
    "merchant": null,
    "date": null,
    "amount": null,
    "category": "Other",
    "items": []
}
"""