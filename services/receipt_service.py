"""
SpendShield AI - Receipt Service

Handles receipt extraction and validation.
"""

import streamlit as st

from services import gemini_service


def extract_receipt_data(image_data):
    """
    Extract receipt data using Gemini Vision.
    """

    try:

        if image_data is None:
            st.error("❌ No receipt image provided.")
            return None

        result = gemini_service.extract_receipt_data(
            image_data
        )

        if result is None:
            st.error(
                "❌ Gemini could not extract receipt data."
            )
            return None

        return result

    except Exception as e:

        st.error(
            f"❌ Receipt extraction failed: {str(e)}"
        )

        return None


def validate_receipt_data(data):
    """
    Validate extracted receipt data.
    """

    if not data:
        return False

    merchant = data.get("merchant")
    amount = data.get("amount")

    if not merchant:
        return False

    if amount is None:
        return False

    try:

        amount = float(amount)

        if amount <= 0:
            return False

    except (
        ValueError,
        TypeError
    ):

        return False

    return True