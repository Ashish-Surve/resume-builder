"""Progress tracking component."""

import streamlit as st
from typing import Dict


def render_progress_sidebar(current_stage: int, stage_status: Dict[int, str]) -> None:
    """Render progress sidebar with stage status.

    Args:
        current_stage: Current stage number (0-3)
        stage_status: Dict mapping stage numbers to status strings
    """
    with st.sidebar:
        st.header("📋 Progress")
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

            # Determine color/styling
            if i == current_stage:
                st.markdown(f"### {icon} **Stage {i+1}: {stage_title}**")
                st.markdown(f"_{stage_desc}_")
            elif i < current_stage:
                st.markdown(f"{icon} **Stage {i+1}: {stage_title}**")
            else:
                st.markdown(f"{icon} Stage {i+1}: {stage_title}")

            if i < len(stages) - 1:
                st.divider()

        st.divider()
        st.markdown(f"**Current:** Stage {current_stage + 1} of 4")
