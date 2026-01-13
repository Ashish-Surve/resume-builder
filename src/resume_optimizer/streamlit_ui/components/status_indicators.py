"""Status indicator components for the UI."""

import streamlit as st
from datetime import datetime, timedelta
from typing import Optional


def render_auto_save_indicator():
    """Render auto-save status indicator in sidebar."""
    last_save = st.session_state.get('last_auto_save')

    if last_save:
        time_since_save = datetime.now() - last_save
        if time_since_save < timedelta(seconds=5):
            st.sidebar.success("✓ Saved")
        elif time_since_save < timedelta(minutes=1):
            st.sidebar.caption(f"Last saved {int(time_since_save.total_seconds())}s ago")
        else:
            minutes_ago = int(time_since_save.total_seconds() / 60)
            st.sidebar.caption(f"Last saved {minutes_ago}m ago")


def render_resume_selector():
    """Render resume selector dropdown in sidebar."""
    from resume_optimizer.streamlit_ui.utils.storage import BrowserStorage

    st.sidebar.divider()
    st.sidebar.subheader("📂 Saved Resumes")

    resume_list = BrowserStorage.get_resume_list()

    if not resume_list:
        st.sidebar.caption("No saved resumes yet")
        return

    # Current resume ID
    current_id = BrowserStorage.get_current_resume_id()

    # Create options for selectbox
    resume_options = {}
    for resume in resume_list:
        display_name = f"{resume['applicant_name']}"
        if resume['company_name']:
            display_name += f" → {resume['company_name']}"
        display_name += f" ({resume['file_name']})"
        resume_options[display_name] = resume['id']

    # Find current index
    current_index = 0
    if current_id:
        for idx, (_, resume_id) in enumerate(resume_options.items()):
            if resume_id == current_id:
                current_index = idx
                break

    # Select resume
    selected_display = st.sidebar.selectbox(
        "Switch Resume",
        list(resume_options.keys()),
        index=current_index,
        key="resume_selector_dropdown"
    )

    selected_id = resume_options[selected_display]

    # If selection changed, load the resume
    if selected_id != current_id:
        resume_data = BrowserStorage.load_resume_data(selected_id)
        if resume_data:
            # Load into session state
            st.session_state.resume_data_raw = resume_data['resume_data_raw']
            st.session_state.resume_data_edited = resume_data['resume_data_edited']
            st.session_state.applicant_name = resume_data['applicant_name']
            st.session_state.company_name = resume_data['company_name']
            st.session_state.uploaded_file_name = resume_data.get('file_name')

            BrowserStorage.set_current_resume(selected_id)
            st.rerun()

    # Delete button for current resume
    col1, col2 = st.sidebar.columns([3, 1])
    with col2:
        if st.button("🗑️", help="Delete selected resume", key="delete_resume_btn"):
            if len(resume_list) > 1:
                BrowserStorage.delete_resume(selected_id)
                st.rerun()
            else:
                st.sidebar.error("Cannot delete last resume")
