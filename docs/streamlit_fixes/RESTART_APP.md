# Restarting the Streamlit App

## Issue: White Screen or Port Already in Use

If you're seeing a white screen or "Port 8501 is already in use" error:

### Step 1: Kill Old Streamlit Process

```bash
# Kill the old process
pkill -f "streamlit run"

# Or more forcefully
killall python3
```

### Step 2: Clear Streamlit Cache (Optional)

```bash
rm -rf ~/.streamlit/
```

### Step 3: Restart the App

```bash
# Make sure dependencies are installed
uv sync

# Option 1: Using the run script
./run.sh

# Option 2: Direct command
uv run streamlit run src/resume_optimizer/streamlit_ui/app.py

# Option 3: Using main.py
uv run python main.py
```

### Step 4: Check the App

Open your browser to: **http://localhost:8501**

You should see:
- A header: "🚀 AI-Powered Resume Optimizer"
- A sidebar with progress tracking
- Stage 1 content below

## Common Issues

### Still Getting White Screen?

1. Check the terminal for error messages
2. Make sure all dependencies are installed: `uv sync`
3. Check that the URL is correct: `http://localhost:8501` (not just `localhost:8501`)
4. Try a different port: `streamlit run src/resume_optimizer/streamlit_ui/app.py --server.port=8502`

### Port Stuck?

```bash
# Find and kill the process using port 8501
lsof -i :8501 | grep LISTEN | awk '{print $2}' | xargs kill -9
```

### Import Errors?

Make sure you're running from the project root:
```bash
cd /Users/devwork/Developer/Project/resume-builder
uv run streamlit run src/resume_optimizer/streamlit_ui/app.py
```

## Fixed Issues in This Version

✅ **st.set_page_config() positioning** - Now called first before any other Streamlit commands
✅ **sys.path handling** - Now properly adds src directory for imports
✅ **All files recompiled** - Zero syntax errors verified
✅ **Subprocess launching** - main.py now uses subprocess instead of internal CLI

## What You Should See

When the app starts:
1. Terminal shows: "You can now view your Streamlit app in your browser"
2. Browser shows the app with:
   - Header with app title
   - Left sidebar with progress
   - Stage 1 form for uploading resume
3. No errors or white screen

## If Still Having Issues

1. Check terminal output for specific error messages
2. Run: `uv sync` to ensure all dependencies installed
3. Try with a fresh terminal: `exit` then open new terminal
4. Check Python version: `python --version` (should be 3.9+)
5. Report the error message from the terminal

## Quick Restart Command

```bash
# One-liner to kill and restart
pkill -f "streamlit run" 2>/dev/null; sleep 1; ./run.sh
```
