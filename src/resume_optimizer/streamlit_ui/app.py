
# src/resume_optimizer/streamlit_ui/app.py
"""
Main Streamlit application for Resume Optimizer.
Implements MVC pattern with clean separation of concerns.
"""

import streamlit as st
import logging
import uuid

# Configure page
st.set_page_config(
    page_title="AI Resume Optimizer",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)


class ResumeOptimizerApp:
    """Main application class managing the Streamlit interface."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.setup_logging()
        self.initialize_session_state()

    def setup_logging(self) -> None:
        """Configure logging for the application."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

    def initialize_session_state(self) -> None:
        """Initialize Streamlit session state variables."""
        if 'session_id' not in st.session_state:
            st.session_state.session_id = str(uuid.uuid4())

        if 'step' not in st.session_state:
            st.session_state.step = 'upload'

        if 'resume_data' not in st.session_state:
            st.session_state.resume_data = None

        if 'job_data' not in st.session_state:
            st.session_state.job_data = None

    def run(self) -> None:
        """Main application entry point."""
        try:
            # Header
            self.render_header()

            # Sidebar
            self.render_sidebar()

            # Main content
            if st.session_state.step == 'upload':
                self.render_upload_step()
            elif st.session_state.step == 'configure':
                self.render_configure_step()
            elif st.session_state.step == 'processing':
                self.render_processing_step()
            elif st.session_state.step == 'results':
                self.render_results_step()

        except Exception as e:
            self.logger.error(f"Application error: {e}")
            st.error(f"An error occurred: {e}")

    def render_header(self) -> None:
        """Render application header."""
        st.title("🚀 AI-Powered Resume Optimizer")
        st.markdown("---")
        st.markdown("""
        **Transform your resume with AI-powered optimization for better ATS compatibility and job matching.**

        This tool analyzes your resume against specific job descriptions and provides personalized recommendations 
        to improve your chances of getting past Applicant Tracking Systems (ATS).
        """)

    def render_sidebar(self) -> None:
        """Render sidebar with navigation and information."""
        with st.sidebar:
            st.header("📋 Process Steps")

            steps = [
                ("📤 Upload Documents", 'upload'),
                ("⚙️ Configure Settings", 'configure'),
                ("🔄 Processing", 'processing'),
                ("📊 View Results", 'results')
            ]

            for i, (label, step_key) in enumerate(steps, 1):
                if st.session_state.step == step_key:
                    st.markdown(f"**{i}. {label}** ⬅️")
                else:
                    st.markdown(f"{i}. {label}")

    def render_upload_step(self) -> None:
        """Render document upload step."""
        st.header("📤 Step 1: Upload Your Documents")

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("📄 Resume Upload")
            resume_file = st.file_uploader(
                "Choose your resume file",
                type=['pdf', 'docx', 'txt'],
                help="Upload your current resume in PDF, DOCX, or TXT format"
            )

            if resume_file is not None:
                st.success("✅ Resume uploaded successfully!")
                st.session_state.resume_data = resume_file

        with col2:
            st.subheader("💼 Job Description")
            job_text = st.text_area(
                "Paste the job description here",
                height=300,
                help="Copy and paste the complete job description"
            )

            if job_text and len(job_text.strip()) > 50:
                st.success("✅ Job description provided!")
                st.session_state.job_data = job_text

        # Navigation
        st.markdown("---")
        if st.session_state.resume_data and st.session_state.job_data:
            if st.button("➡️ Continue to Configuration", type="primary"):
                st.session_state.step = 'configure'
                st.rerun()
        else:
            st.info("👆 Please upload both resume and job description to continue")

    def render_configure_step(self) -> None:
        """Render configuration step."""
        st.header("⚙️ Step 2: Configure Optimization Settings")

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("👤 Personal Information")
            applicant_name = st.text_input(
                "Your Full Name",
                help="This will appear on the optimized resume"
            )

            company_name = st.text_input(
                "Target Company Name",
                help="The company you're applying to"
            )

        with col2:
            st.subheader("🎯 Optimization Options")

            optimization_focus = st.multiselect(
                "Focus Areas",
                ["Keyword Optimization", "ATS Compatibility", "Skill Alignment", "Content Quality"],
                default=["Keyword Optimization", "ATS Compatibility"]
            )

        # Navigation
        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ Back to Upload"):
                st.session_state.step = 'upload'
                st.rerun()

        with col2:
            if applicant_name and company_name:
                if st.button("🚀 Start Optimization", type="primary"):
                    st.session_state.applicant_name = applicant_name
                    st.session_state.company_name = company_name
                    st.session_state.step = 'processing'
                    st.rerun()
            else:
                st.warning("Please provide your name and target company")

    def render_processing_step(self) -> None:
        """Render processing step with progress indicators."""
        st.header("🔄 Step 3: Processing Your Resume")

        # Processing status
        progress_bar = st.progress(0)
        status_text = st.empty()

        # Simulate processing steps
        processing_steps = [
            ("Parsing documents", 20),
            ("Analyzing job requirements", 40),
            ("Running ATS compatibility check", 60),
            ("Optimizing content with AI", 80),
            ("Generating optimized resume", 100)
        ]

        try:
            for i, (step_desc, progress) in enumerate(processing_steps):
                status_text.text(f"⚙️ {step_desc}...")
                progress_bar.progress(progress)

                import time
                time.sleep(1)  # Simulate processing time

            status_text.text("✅ Processing completed successfully!")

            # Show completion message
            st.success("🎉 Your resume has been optimized!")

            # Mock results for demonstration
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("ATS Score Improvement", "+15.2", delta="85.2/100")
            with col2:
                st.metric("Compatibility Score", "92%")
            with col3:
                st.metric("Improvements Found", "7")

            if st.button("📊 View Detailed Results", type="primary"):
                st.session_state.step = 'results'
                st.rerun()

        except Exception as e:
            st.error(f"Processing failed: {e}")

            if st.button("🔄 Retry Processing"):
                st.rerun()

    def render_results_step(self) -> None:
        """Render results and download step."""
        st.header("📊 Step 4: Optimization Results")

        # Results overview
        st.subheader("📈 Optimization Overview")

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Original Score", "70.0/100")

        with col2:
            st.metric("Optimized Score", "85.2/100", delta="+15.2")

        with col3:
            st.metric("ATS Compatibility", "92%")

        with col4:
            st.metric("Missing Keywords", "3")

        # Detailed results
        tab1, tab2, tab3, tab4 = st.tabs(["📋 Recommendations", "🔑 Keywords", "📊 Analysis", "📄 Download"])

        with tab1:
            st.subheader("💡 Optimization Recommendations")
            recommendations = [
                "Add more technical keywords related to the job requirements",
                "Improve the professional summary section",
                "Use standard section headers for better ATS parsing",
                "Include quantified achievements in experience descriptions",
                "Add relevant skills mentioned in the job description"
            ]
            for i, rec in enumerate(recommendations, 1):
                st.write(f"{i}. {rec}")

        with tab2:
            st.subheader("🔑 Keyword Analysis")

            col1, col2 = st.columns(2)
            with col1:
                st.write("**Missing Keywords:**")
                missing_keywords = ["Machine Learning", "Python", "Data Analysis"]
                for keyword in missing_keywords:
                    st.write(f"• {keyword}")

            with col2:
                st.write("**Matched Keywords:**")
                matched_keywords = ["Project Management", "Leadership", "Communication"]
                for keyword in matched_keywords:
                    st.write(f"✅ {keyword}")

        with tab3:
            st.subheader("📊 Detailed Analysis")
            st.write("**Improvements Applied:**")
            improvements = [
                "Enhanced keyword density by 25%",
                "Improved ATS compatibility score",
                "Strengthened skill alignment with job requirements"
            ]
            for improvement in improvements:
                st.write(f"✅ {improvement}")

        with tab4:
            st.subheader("📄 Download Optimized Resume")

            # Generate PDF button
            if st.button("🎯 Generate ATS-Optimized PDF", type="primary"):
                with st.spinner("Generating PDF..."):
                    import time
                    time.sleep(2)  # Simulate PDF generation
                    st.success("✅ PDF generated successfully!")

                    # Mock download button
                    st.download_button(
                        label="⬇️ Download Optimized Resume",
                        data=b"Mock PDF content",
                        file_name="optimized_resume.pdf",
                        mime="application/pdf"
                    )

            st.info("💡 **Pro Tip:** The generated PDF follows ATS best practices including standard fonts, clear sections, and proper formatting.")

        # Navigation
        st.markdown("---")
        col1, col2 = st.columns(2)

        with col1:
            if st.button("🔄 Optimize Another Resume"):
                # Reset for new session
                for key in list(st.session_state.keys()):
                    if key not in ['session_id']:
                        del st.session_state[key]
                st.rerun()


def main():
    """Main application entry point."""
    try:
        app = ResumeOptimizerApp()
        app.run()
    except Exception as e:
        st.error(f"Application failed to start: {e}")
        logging.error(f"Application startup error: {e}")


if __name__ == "__main__":
    main()
