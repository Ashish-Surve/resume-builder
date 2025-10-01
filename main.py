
# main.py
"""
Main entry point for the Resume Optimizer application.
Handles application initialization and error handling.
"""

import sys
import logging
from pathlib import Path
import argparse

# Add src to path for imports
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))


def setup_logging(debug: bool = False) -> None:
    """Configure application logging."""
    log_level = logging.DEBUG if debug else logging.INFO

    # Create logs directory
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    # Configure logging
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / "resume_optimizer.log"),
            logging.StreamHandler(sys.stdout)
        ]
    )


def validate_environment() -> None:
    """Validate environment and configuration."""
    try:
        # Check required directories
        data_dir = Path("data")
        if not data_dir.exists():
            data_dir.mkdir(parents=True, exist_ok=True)
            logging.info(f"Created data directory: {data_dir}")

        temp_dir = Path("data/temp")
        if not temp_dir.exists():
            temp_dir.mkdir(parents=True, exist_ok=True)
            logging.info(f"Created temp directory: {temp_dir}")

        logging.info("Environment validation completed successfully")

    except Exception as e:
        logging.error(f"Environment validation failed: {e}")
        raise


def run_streamlit_app() -> None:
    """Launch the Streamlit application."""
    import streamlit.web.cli as stcli
    import sys

    try:
        logging.info("Starting Resume Optimizer Streamlit application...")

        # Set up streamlit arguments
        sys.argv = [
            "streamlit", 
            "run", 
            str(Path("src") / "resume_optimizer" / "streamlit_ui" / "app.py"),
            "--server.port=8501",
            "--server.address=localhost"
        ]

        # Run streamlit
        stcli.main()

    except Exception as e:
        logging.error(f"Streamlit application failed: {e}")
        raise


def main() -> None:
    """Main application entry point."""
    parser = argparse.ArgumentParser(
        description="AI-Powered Resume Optimizer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run Streamlit UI (default)
  python main.py

  # Run with debug logging
  python main.py --debug
        """
    )

    parser.add_argument("--debug", action="store_true", help="Enable debug logging")

    args = parser.parse_args()

    try:
        # Setup logging
        setup_logging(args.debug)

        # Validate environment
        validate_environment()

        # Run Streamlit app
        run_streamlit_app()

    except KeyboardInterrupt:
        logging.info("Application interrupted by user")
        sys.exit(0)
    except Exception as e:
        logging.error(f"Unexpected error: {e}", exc_info=True)
        print(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
