"""Common UI components shared across the application."""

import streamlit as st


def render_header() -> None:
    """Render the main application header."""
    st.title("🚀 AI-Powered Resume Optimizer")
    st.markdown("---")
    st.markdown("""
    **Optimize your resume with AI to improve ATS compatibility and job matching.**

    4-stage workflow: Parse → Analyze → Optimize → Download
    """)


def render_navigation_buttons(
    back_enabled: bool = True,
    forward_enabled: bool = True,
    forward_text: str = "Continue",
    on_back: callable = None,
    on_forward: callable = None
) -> None:
    """Render navigation buttons with consistent styling.

    Args:
        back_enabled: Whether back button is enabled
        forward_enabled: Whether forward button is enabled
        forward_text: Text for forward button
        on_back: Callback for back button
        on_forward: Callback for forward button
    """
    col1, col2 = st.columns(2)

    with col1:
        if st.button("⬅️ Back", disabled=not back_enabled):
            if on_back:
                on_back()
            else:
                st.session_state.current_stage -= 1
                st.rerun()

    with col2:
        if st.button(f"➡️ {forward_text}", type="primary", disabled=not forward_enabled):
            if on_forward:
                on_forward()
            else:
                st.session_state.current_stage += 1
                st.rerun()
