"""Validation UI component for displaying validation results."""

import streamlit as st
from typing import List


def render_validation_results(is_valid: bool, errors: List[str]) -> None:
    """Display validation results.

    Args:
        is_valid: Whether validation passed
        errors: List of error messages if validation failed
    """
    if is_valid:
        st.success("✅ All validation checks passed!")
    else:
        st.error("❌ Validation failed. Please fix the following issues:")
        for error in errors:
            st.markdown(f"- {error}")
