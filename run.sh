#!/bin/bash
# Quick setup and run script for Resume Optimizer Streamlit UI

set -e

echo "📦 Resume Optimizer Streamlit UI"
echo "================================="
echo ""

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "❌ uv is not installed"
    echo "Install it with: pip install uv"
    exit 1
fi

echo "✓ uv found"

# Check if dependencies are installed
if ! uv run python -c "import streamlit" 2>/dev/null; then
    echo "📥 Installing dependencies..."
    uv sync
    echo "✓ Dependencies installed"
else
    echo "✓ Dependencies already installed"
fi

echo ""
echo "🚀 Starting Streamlit app..."
echo "   App will open at: http://localhost:8501"
echo ""

# Run the app
uv run streamlit run src/resume_optimizer/streamlit_ui/app.py
