#!/bin/bash
# Start the Resume Optimizer Streamlit app with proper path setup

set -e

echo "🚀 Starting Resume Optimizer Streamlit UI"
echo "=========================================="
echo ""

# Change to project root
cd "$(dirname "$0")"

# Kill any existing streamlit processes
echo "Cleaning up old processes..."
pkill -f "streamlit run" 2>/dev/null || true
sleep 1

# Ensure dependencies are installed
echo "Checking dependencies..."
uv sync -q

echo ""
echo "Starting app on http://localhost:8501"
echo "Press Ctrl+C to stop"
echo ""

# Run streamlit with PYTHONPATH set
export PYTHONPATH="src:$PYTHONPATH"
exec uv run streamlit run src/resume_optimizer/streamlit_ui/app.py
