"""
SpendShield AI - Gemini Service

Responsible for:
- AI spending analysis
- Financial roast generation
- Recovery-plan generation
- Receipt information extraction

Gemini handles AI interpretation.
Python/Pandas handles deterministic financial calculations.
"""

import io
import json
import os
import re
from typing import Any, Optional

import pandas as pd
import streamlit as st
from PIL import Image
from google import genai
from google.genai import types
from dotenv import load_dotenv

from utils import prompts
load_dotenv()
load_dotenv("../.env")


# =========================================================
# CONFIGURATION
# =========================================================

GEMINI_MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-3.6-flash"
)

RECEIPT_MODEL = os.getenv(
    "GEMINI_RECEIPT_MODEL",
    "gemini-3.6-flash"
)


# =========================================================
# GEMINI CLIENT
# =========================================================

def get_gemini_client() -> Optional[genai.Client]:
    """
    Create Gemini client using environment variable
    or Streamlit secrets.
    """

    api_key = os.getenv("GEMINI_API_KEY")

    # Streamlit secrets fallback
    if not api_key:
        try:
            api_key = st.secrets.get(
                "GEMINI_API_KEY",
                None
            )
        except Exception:
            api_key = None

    if not api_key:
        st.error(
            "❌ GEMINI_API_KEY was not found."
        )
        return None

    try:
        client = genai.Client(
            api_key=api_key
        )

        return client

    except Exception as e:
        st.error(
            f"❌ Failed to initialize Gemini: {str(e)}"
        )
        return None


# =========================================================
# GENERAL RESPONSE HELPERS
# =========================================================

def _extract_text(response) -> str:
    """
    Safely extract text from Gemini response.
    """

    if response is None:
        return ""

    try:
        text = response.text

        if text:
            return str(text).strip()

    except Exception:
        pass

    return ""


def _parse_json_response(text: str) -> Optional[dict]:
    """
    Parse JSON returned by Gemini.

    Handles:
    - normal JSON
    - ```json ... ```
    - JSON surrounded by extra text
    """

    if not text:
        return None

    cleaned = text.strip()

    # Remove markdown code fences
    if cleaned.startswith("```"):
        cleaned = re.sub(
            r"^```(?:json)?\s*",
            "",
            cleaned,
            flags=re.IGNORECASE
        )

        cleaned = re.sub(
            r"\s*```$",
            "",
            cleaned
        )

        cleaned = cleaned.strip()

    # Try direct JSON
    try:
        parsed = json.loads(cleaned)

        if isinstance(parsed, dict):
            return parsed

    except json.JSONDecodeError:
        pass

    # Try extracting JSON object
    start = cleaned.find("{")
    end = cleaned.rfind("}")

    if start != -1 and end > start:

        candidate = cleaned[start:end + 1]

        try:
            parsed = json.loads(candidate)

            if isinstance(parsed, dict):
                return parsed

        except json.JSONDecodeError:
            pass

    return None


# =========================================================
# SPENDING ANALYSIS
# =========================================================

def analyze_spending(
    df: pd.DataFrame
) -> Optional[dict[str, Any]]:
    """
    Analyze spending using Gemini.

    Returns:

    {
        "roast": "...",
        "recovery_plan": {...},
        "raw_response": "..."
    }
    """

    if df is None or df.empty:
        st.error("❌ No expense data available.")
        return None

    client = get_gemini_client()

    if client is None:
        return None

    try:

        # Build verified financial context
        context = prompts.build_analysis_context(df)

        # -------------------------------------------------
        # Generate Roast
        # -------------------------------------------------

        roast_prompt = prompts.get_roast_prompt(
            context
        )

        roast_response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=roast_prompt
        )

        roast = _extract_text(
            roast_response
        )

        # -------------------------------------------------
        # Generate Recovery Plan
        # -------------------------------------------------

        recovery_prompt = prompts.get_recovery_plan_prompt(
            context
        )

        recovery_response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=recovery_prompt
        )

        recovery_text = _extract_text(
            recovery_response
        )

        recovery_plan = _parse_json_response(
            recovery_text
        )

        if recovery_plan is None:

            recovery_plan = {
                "summary": recovery_text,
                "top_leaks": [],
                "recommended_cuts": [],
                "monthly_savings": 0,
                "annual_savings": 0,
                "priority_actions": [],
                "weekly_challenge": ""
            }

        return {
            "roast": roast,
            "recovery_plan": recovery_plan,
            "raw_response": recovery_text
        }

    except Exception as e:

        st.error(
            f"❌ Gemini analysis failed: {str(e)}"
        )

        return None


# =========================================================
# RECEIPT EXTRACTION
# =========================================================

def extract_receipt_data(image_data):
    """
    Extract transaction information from a receipt image.

    image_data should be a Streamlit UploadedFile
    returned by st.file_uploader() or st.camera_input().
    """

    client = get_gemini_client()

    if client is None:
        return None

    if image_data is None:
        st.error(
            "❌ No receipt image was provided."
        )
        return None

    try:

        # -------------------------------------------------
        # READ IMAGE BYTES
        # -------------------------------------------------

        image_bytes = image_data.getvalue()

        if not image_bytes:
            st.error(
                "❌ The uploaded receipt image is empty."
            )
            return None

        # Get MIME type supplied by Streamlit
        mime_type = getattr(
            image_data,
            "type",
            None
        )

        # Fallback MIME type
        if not mime_type:
            mime_type = "image/jpeg"

        # -------------------------------------------------
        # VERIFY IMAGE
        # -------------------------------------------------

        try:

            image = Image.open(
                io.BytesIO(image_bytes)
            )

            # Force PIL to actually read the image
            image.load()

        except Exception as e:

            st.error(
                f"❌ Could not read receipt image: {str(e)}"
            )

            return None

        # -------------------------------------------------
        # RECEIPT PROMPT
        # -------------------------------------------------

        receipt_prompt = """
You are an expert receipt OCR and financial transaction
extraction system.

Carefully inspect the ENTIRE receipt image.

Extract the transaction information from the image.

Return ONLY valid JSON.

Use exactly this structure:

{
    "merchant": "string or null",
    "date": "YYYY-MM-DD or null",
    "amount": number or null,
    "category": "Food | Transport | Shopping | Entertainment | Utilities | Health | Housing | Dining | Other",
    "items": ["item 1", "item 2"]
}

IMPORTANT RULES:

1. MERCHANT
Extract the actual store, restaurant, company, or merchant
name visible on the receipt.

2. DATE
Find the transaction/purchase date.
Convert it to YYYY-MM-DD.

If the date is not visible or cannot be determined,
return null.

3. AMOUNT
Find the FINAL TOTAL actually paid.

Do NOT use:
- subtotal
- tax
- discount
- individual item price
- quantity price

For example:

₹1,249.50

must become:

1249.50

Return a NUMBER, not a string.

4. CATEGORY

Choose exactly ONE:

Food
Transport
Shopping
Entertainment
Utilities
Health
Housing
Dining
Other

5. ITEMS
Extract visible purchased items.

If individual items cannot be determined,
return an empty list.

6. DO NOT INVENT INFORMATION.

If something cannot be read clearly:
- use null for merchant/date/amount
- use [] for items

7. Inspect the whole image carefully before answering.

Return JSON only.
Do not include markdown.
Do not include ```json.
Do not explain anything outside the JSON.
"""

        # -------------------------------------------------
        # CREATE GEMINI IMAGE PART
        # -------------------------------------------------

        image_part = types.Part.from_bytes(
            data=image_bytes,
            mime_type=mime_type
        )

        # -------------------------------------------------
        # CALL GEMINI
        # -------------------------------------------------

        response = client.models.generate_content(
            model=RECEIPT_MODEL,
            contents=[
                receipt_prompt,
                image_part
            ],
            config=types.GenerateContentConfig(
                temperature=0,
                response_mime_type="application/json"
            )
        )

        # -------------------------------------------------
        # GET RESPONSE TEXT
        # -------------------------------------------------

        response_text = _extract_text(
            response
        )

        # DEBUG INFORMATION
        if not response_text:

            st.error(
                "❌ Gemini returned an empty response."
            )

            # This helps identify API/model problems
            st.write(
                "Gemini response object:"
            )
            st.write(response)

            return None

        # -------------------------------------------------
        # PARSE JSON
        # -------------------------------------------------

        data = _parse_json_response(
            response_text
        )

        if data is None:

            st.error(
                "❌ Gemini returned invalid JSON."
            )

            st.write(
                "Raw Gemini response:"
            )

            st.code(
                response_text
            )

            return None

        # -------------------------------------------------
        # VALIDATE + NORMALIZE
        # -------------------------------------------------

        data = _validate_receipt_data(
            data
        )

        # -------------------------------------------------
        # DEBUG
        # -------------------------------------------------

        return data

    except Exception as e:

        st.error(
            f"❌ Receipt extraction failed: {str(e)}"
        )

        return None


# =========================================================
# RECEIPT VALIDATION
# =========================================================

def _validate_receipt_data(
    data: dict
) -> dict:
    """
    Validate and normalize extracted receipt data.
    """

    result = {
        "merchant": data.get(
            "merchant"
        ),
        "date": data.get(
            "date"
        ),
        "amount": data.get(
            "amount"
        ),
        "category": data.get(
            "category"
        ),
        "items": data.get(
            "items",
            []
        )
    }

    # -----------------------------------------------------
    # NORMALIZE MERCHANT
    # -----------------------------------------------------

    if result["merchant"] is not None:

        result["merchant"] = str(
            result["merchant"]
        ).strip()

    # -----------------------------------------------------
    # NORMALIZE DATE
    # -----------------------------------------------------

    if result["date"] is not None:

        result["date"] = str(
            result["date"]
        ).strip()

    # -----------------------------------------------------
    # NORMALIZE CATEGORY
    # -----------------------------------------------------

    if result["category"] is not None:

        result["category"] = str(
            result["category"]
        ).strip()

    # -----------------------------------------------------
    # NORMALIZE AMOUNT
    # -----------------------------------------------------

    amount = result["amount"]

    if amount is not None:

        try:

            amount_string = str(
                amount
            )

            amount_string = (
                amount_string
                .replace(",", "")
                .replace("₹", "")
                .replace("$", "")
                .strip()
            )

            result["amount"] = float(
                amount_string
            )

        except (
            ValueError,
            TypeError
        ):

            result["amount"] = None

    # -----------------------------------------------------
    # NORMALIZE ITEMS
    # -----------------------------------------------------

    if not isinstance(
        result["items"],
        list
    ):

        result["items"] = []

    # Convert items to strings
    result["items"] = [
        str(item).strip()
        for item in result["items"]
        if item is not None
    ]

    return result


# =========================================================
# CONNECTION TEST
# =========================================================

def test_gemini_connection() -> bool:
    """
    Check whether Gemini client can be initialized.
    """

    client = get_gemini_client()

    return client is not None