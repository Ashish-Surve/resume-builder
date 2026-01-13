"""Progress tracking component with clickable navigation."""

import streamlit as st
from typing import Dict


def render_progress_sidebar(current_stage: int, stage_status: Dict[int, str]) -> None:
    """Render progress sidebar with clickable stage navigation.

    Args:
        current_stage: Current stage number (0-3)
        stage_status: Dict mapping stage numbers to status strings
    """
    # Import here to avoid circular dependency
    from resume_optimizer.streamlit_ui.utils.storage import ProgressTracker
    from resume_optimizer.streamlit_ui.components.status_indicators import (
        render_auto_save_indicator,
        render_resume_selector
    )

    with st.sidebar:
        st.header("📋 Progress")

        # Progress percentage
        progress_pct = ProgressTracker.calculate_progress()
        st.progress(progress_pct / 100.0)
        st.caption(f"Overall Progress: {progress_pct:.0f}%")

        # Auto-save indicator
        render_auto_save_indicator()

        st.divider()

        stages = [
            ("Resume Parsing", "Parse your resume"),
            ("Job Analysis", "Analyze job description"),
            ("ATS Optimization", "Optimize resume"),
            ("PDF Generation", "Download final resume")
        ]

        for i, (stage_title, stage_desc) in enumerate(stages):
            status = stage_status.get(i, 'pending')

            # Determine icon based on status
            if status == 'completed':
                icon = "✅"
            elif i == current_stage:
                icon = "▶️"
            else:
                icon = "⭕"

            # Check if stage is accessible
            is_accessible = ProgressTracker.is_stage_accessible(i)
            accessibility_msg = ProgressTracker.get_stage_accessibility_message(i)

            # Create clickable button for navigation
            button_label = f"{icon} Stage {i+1}: {stage_title}"

            # Determine styling
            if i == current_stage:
                st.markdown(f"### **{button_label}**")
                st.caption(stage_desc)
            else:
                # Make it clickable
                button_key = f"nav_stage_{i}"

                if not is_accessible:
                    # Show disabled button with tooltip
                    st.button(
                        button_label,
                        disabled=True,
                        key=button_key,
                        help=accessibility_msg,
                        use_container_width=True
                    )
                else:
                    # Clickable navigation button
                    if st.button(
                        button_label,
                        key=button_key,
                        help=f"Go to {stage_title}",
                        use_container_width=True
                    ):
                        st.session_state.current_stage = i
                        st.rerun()

            if i < len(stages) - 1:
                st.divider()

        st.divider()
        st.markdown(f"**Current:** Stage {current_stage + 1} of 4")

        # Resume selector
        render_resume_selector()
