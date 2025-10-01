# /// script
# dependencies = [
#   "argparse",
# ]
# ///

"""
UV-based Setup Script for AI Resume Optimizer Project

Transforms exported-assets folder into a complete uv-managed Python project structure.
Leverages uv's modern project management capabilities including pyproject.toml,
automatic virtual environment creation, and dependency management.

Usage:
    python setup_project_uv.py --assets ./exported-assets --project-name resume-optimizer
    
Features:
- Creates uv-compatible project structure with src/ layout
- Maps exported assets to appropriate destinations  
- Generates comprehensive pyproject.toml with all dependencies
- Sets up development environment with uv sync
- Creates proper .gitignore and .python-version files
"""

import argparse
import shutil
from pathlib import Path
import sys
import subprocess

# -------------------------
# UV-specific helpers
# -------------------------

def run_uv_command(cmd: list[str], cwd: Path = None, check: bool = True):
    """Run a uv command and return the result."""
    try:
        result = subprocess.run(
            cmd, 
            cwd=cwd, 
            check=check, 
            capture_output=True, 
            text=True
        )
        return result
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Command failed: {' '.join(cmd)}")
        print(f"[ERROR] Output: {e.stdout}")
        print(f"[ERROR] Error: {e.stderr}")
        if check:
            sys.exit(1)
        return e

def check_uv_installed():
    """Check if uv is installed and available."""
    try:
        result = subprocess.run(["uv", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"[INFO] Found uv: {result.stdout.strip()}")
            return True
    except FileNotFoundError:
        pass
    
    print("[ERROR] uv is not installed or not in PATH")
    print("[INFO] Install uv from: https://docs.astral.sh/uv/getting-started/installation/")
    return False

def safe_write_text(path: Path, content: str, overwrite: bool = False):
    """Write text to file with directory creation."""
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and not overwrite:
        print(f"[SKIP] File exists: {path}")
        return False
    path.write_text(content, encoding="utf-8")
    print(f"[CREATED] {path}")
    return True

def safe_copy(src: Path, dst: Path, overwrite: bool = False):
    """Copy file/directory safely."""
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists() and not overwrite:
        print(f"[SKIP] Destination exists: {dst}")
        return False
    
    if src.is_file():
        shutil.copy2(src, dst)
        print(f"[COPIED] {src} -> {dst}")
    else:
        if dst.exists() and overwrite:
            shutil.rmtree(dst)
        shutil.copytree(src, dst, dirs_exist_ok=True)
        print(f"[COPIED] {src}/ -> {dst}/")
    return True

def find_and_copy_asset(assets_dir: Path, patterns: list[str], destination: Path, 
                       rename_to: str = None, overwrite: bool = False):
    """Find first matching asset and copy to destination."""
    matches = []
    for pattern in patterns:
        matches.extend(assets_dir.rglob(pattern))
    
    if not matches:
        return None
    
    # Use the shortest path (likely the main file)
    src = sorted(matches, key=lambda p: len(str(p)))[0]
    dst = destination if rename_to is None else destination.with_name(rename_to)
    
    if safe_copy(src, dst, overwrite=overwrite):
        return dst
    return None

# -------------------------
# UV Project Content Templates
# -------------------------

def get_pyproject_toml_content(project_name: str) -> str:
    """Generate comprehensive pyproject.toml for uv project."""
    normalized_name = project_name.lower().replace("-", "_")
    
    return f"""[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "{project_name}"
version = "0.1.0"
description = "AI-powered resume optimization tool with ATS compatibility checking"
readme = "README.md"
license = {{text = "MIT"}}
requires-python = ">=3.9"
authors = [
    {{name = "Your Name", email = "your.email@example.com"}},
]
keywords = ["resume", "optimization", "ats", "ai", "nlp", "streamlit"]
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: End Users/Desktop",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Topic :: Office/Business",
    "Topic :: Text Processing",
]

# Core dependencies
dependencies = [
    # Web framework
    "streamlit>=1.28.0",
    
    # AI and LangChain
    "langchain>=0.1.0",
    "langchain-community>=0.0.10",
    "langchain-perplexity>=0.1.0",
    "langchain-google-genai>=1.0.0",
    
    # NLP and text processing
    "spacy>=3.7.0",
    "nltk>=3.8.0",
    
    # File processing
    "pypdf>=4.0.0",
    "python-docx>=1.1.0",
    
    # PDF generation
    "reportlab>=4.0.0",
    
    # Data science
    "pandas>=2.1.0",
    "numpy>=1.24.0",
    "scikit-learn>=1.3.0",
    "sentence-transformers>=2.2.0",
    
    # HTTP and API clients
    "requests>=2.31.0",
    "openai>=1.0.0",
    "google-generativeai>=0.3.0",
    
    # Configuration and utilities
    "python-dotenv>=1.0.0",
    "pydantic>=2.0.0",
    "pyyaml>=6.0.0",
]

[project.optional-dependencies]
# Development dependencies
dev = [
    "pytest>=7.4.0",
    "pytest-cov>=4.1.0",
    "pytest-asyncio>=0.21.0",
    "black>=23.7.0",
    "isort>=5.12.0",
    "flake8>=6.0.0",
    "mypy>=1.5.0",
    "pre-commit>=3.0.0",
]

[project.urls]
Homepage = "https://github.com/yourusername/{project_name}"
Repository = "https://github.com/yourusername/{project_name}.git"
Documentation = "https://github.com/yourusername/{project_name}/blob/main/README.md"
"Bug Reports" = "https://github.com/yourusername/{project_name}/issues"

[project.scripts]
{normalized_name} = "{normalized_name}.main:main"
resume-optimizer = "{normalized_name}.main:main"

[tool.uv]
# Development dependencies (uv-specific)
dev-dependencies = [
    "pytest>=7.4.0",
    "pytest-cov>=4.1.0",
    "pytest-asyncio>=0.21.0", 
    "black>=23.7.0",
    "isort>=5.12.0",
    "flake8>=6.0.0",
    "mypy>=1.5.0",
    "pre-commit>=3.0.0",
    "ipython>=8.0.0",
    "jupyter>=1.0.0",
]

[tool.hatchling.build.targets.wheel]
packages = ["src/{normalized_name}"]

# Tool configurations
[tool.black]
line-length = 88
target-version = ['py39']
include = '\\.pyi?$'

[tool.isort]
profile = "black"
multi_line_output = 3
line_length = 88
known_first_party = ["{normalized_name}"]

[tool.flake8]
max-line-length = 88
extend-ignore = ["E203", "W503", "E501"]
exclude = [".git", ".venv", "build", "dist", "__pycache__"]

[tool.mypy]
python_version = "3.9"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
ignore_missing_imports = true

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = "--cov=src --cov-report=html --cov-report=term-missing"
asyncio_mode = "auto"
"""

def get_env_example_content() -> str:
    """Generate .env.example file content."""
    return """# =============================================================================
# AI Resume Optimizer - Environment Configuration
# =============================================================================

# Application Settings
DEBUG=false
DATA_DIR=data
TEMP_DIR=data/temp
MAX_FILE_SIZE=10485760

# AI Service API Keys
# Get Perplexity API key from: https://perplexity.ai/
PERPLEXITY_API_KEY=your_perplexity_api_key_here

# Get Google Gemini API key from: https://makersuite.google.com/
GOOGLE_API_KEY=your_google_api_key_here

# AI Service Settings
AI_MAX_RETRIES=3
AI_TIMEOUT=30
AI_TEMPERATURE=0.7

# Streamlit Configuration
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=localhost

# Logging Settings
LOG_LEVEL=INFO
LOG_FILE=logs/resume_optimizer.log

# =============================================================================
# Setup Instructions:
# 1. Copy this file to .env: cp .env.example .env
# 2. Replace placeholder values with your actual API keys
# 3. Adjust other settings as needed
# 4. Never commit .env to version control
# =============================================================================
"""

def get_gitignore_content() -> str:
    """Generate comprehensive .gitignore file."""
    return """# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# C extensions
*.so

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# UV
uv.lock

# Testing
htmlcov/
.coverage
.pytest_cache/

# Application specific
data/temp/
data/output/
logs/
*.pdf
*.docx
!tests/fixtures/*.pdf
!tests/fixtures/*.docx

# Streamlit
.streamlit/

# IDEs
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
"""

def get_readme_content(project_name: str) -> str:
    """Generate comprehensive README."""
    normalized_name = project_name.lower().replace("-", "_")
    return f"""# {project_name.title()}

AI-powered resume optimization tool with ATS compatibility checking

Transform your resume with intelligent analysis and optimization for better job matching and ATS compatibility.

## Features

- **ATS Optimization**: Improve compatibility with Applicant Tracking Systems
- **AI Analysis**: Leverage Perplexity AI and Google Gemini for intelligent insights
- **Job Matching**: Analyze resume against specific job descriptions
- **Keyword Optimization**: Identify and suggest missing keywords
- **PDF Generation**: Create professionally formatted, ATS-compliant resumes
- **Modern UI**: Clean Streamlit web interface
- **Fast**: Built with uv for lightning-fast dependency management

## Quick Start

### Prerequisites

- Python 3.9+
- [uv](https://docs.astral.sh/uv/getting-started/installation/) (recommended)

### Installation with uv

```bash
# Clone the repository
git clone <repository-url>
cd {project_name}

# Install dependencies and create virtual environment
uv sync

# Download required NLP model
uv run python -m spacy download en_core_web_sm

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys

# Run the application
uv run streamlit run src/{normalized_name}/streamlit_ui/app.py
```

## Project Structure

```
{project_name}/
├── src/{normalized_name}/          # Main package
│   ├── config/              # Configuration management
│   ├── core/                # Core business logic
│   │   ├── resume_parser/   # Resume parsing and extraction
│   │   ├── job_analyzer/    # Job description analysis
│   │   ├── ai_integration/  # AI service clients
│   │   ├── ats_optimizer/   # ATS optimization engine
│   │   └── pdf_generator/   # PDF generation
│   ├── streamlit_ui/        # Web interface
│   └── utils/               # Utilities and helpers
├── tests/                   # Test suite
├── data/                    # Data storage
├── pyproject.toml          # Project configuration
└── README.md               # This file
```

## Configuration

### Required API Keys

Add these to your `.env` file:

- **Perplexity AI**: Get from [https://perplexity.ai/](https://perplexity.ai/)
- **Google Gemini**: Get from [https://makersuite.google.com/](https://makersuite.google.com/)

## Development

### Setup Development Environment

```bash
# Install with development dependencies
uv sync --group dev

# Run tests
uv run pytest

# Format code
uv run black src tests
uv run isort src tests

# Type checking
uv run mypy src
```

### Adding Dependencies

```bash
# Add runtime dependency
uv add package-name

# Add development dependency
uv add --group dev package-name
```

## Testing

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src --cov-report=html
```

## License

This project is licensed under the MIT License.
"""

# -------------------------
# Asset Mapping Rules for UV Project
# -------------------------

def get_asset_mappings(assets_dir: Path, project_root: Path, project_name: str) -> list[dict]:
    """Define mapping rules for exported assets to uv project structure."""
    normalized_name = project_name.lower().replace("-", "_")
    src_root = project_root / "src" / normalized_name
    
    return [
        # Project documentation
        {
            "patterns": ["README*.md", "readme*.md", "README_final.md"],
            "dest": project_root / "README.md"
        },
        {
            "patterns": ["architecture*.md", "architecture-guide.md"],
            "dest": project_root / "docs" / "architecture.md"
        },
        
        # Main application entry point
        {
            "patterns": ["main.py", "main_app_final.py", "main_app_example.py"],
            "dest": project_root / "main.py"
        },
        
        # Streamlit UI
        {
            "patterns": ["streamlit_app_final.py", "streamlit_app_example.py", "app.py"],
            "dest": src_root / "streamlit_ui" / "app.py"
        },
        
        # Core modules
        {
            "patterns": ["config_example.py"],
            "dest": src_root / "config" / "settings.py"
        },
        {
            "patterns": ["exceptions_example.py"],
            "dest": src_root / "utils" / "exceptions.py"
        },
        {
            "patterns": ["models_example.py"],
            "dest": src_root / "core" / "models.py"
        },
        {
            "patterns": ["resume_parser_example.py"],
            "dest": src_root / "core" / "resume_parser" / "parser.py"
        },
        {
            "patterns": ["job_analyzer_example.py"],
            "dest": src_root / "core" / "job_analyzer" / "analyzer.py"
        },
        {
            "patterns": ["ai_integration_example.py"],
            "dest": src_root / "core" / "ai_integration" / "base_client.py"
        },
        {
            "patterns": ["ats_optimizer_example.py"],
            "dest": src_root / "core" / "ats_optimizer" / "optimizer.py"
        },
        {
            "patterns": ["pdf_generator_example.py"],
            "dest": src_root / "core" / "pdf_generator" / "generator.py"
        },
        
        # Data files (sample inputs)
        {
            "patterns": ["*.pdf"],
            "dest": project_root / "data" / "input" / "resumes",
            "bulk": True
        },
        {
            "patterns": ["*.docx", "*.txt"],
            "dest": project_root / "data" / "input" / "job_descriptions", 
            "bulk": True
        },
    ]

# -------------------------
# UV Project Scaffolding
# -------------------------

def create_uv_project_structure(project_root: Path, project_name: str):
    """Create complete uv-compatible project structure."""
    normalized_name = project_name.lower().replace("-", "_")
    src_root = project_root / "src" / normalized_name
    
    # Core directories
    directories = [
        # Source package structure
        src_root / "config",
        src_root / "core",
        src_root / "core" / "resume_parser", 
        src_root / "core" / "job_analyzer",
        src_root / "core" / "ai_integration",
        src_root / "core" / "ats_optimizer",
        src_root / "core" / "pdf_generator",
        src_root / "streamlit_ui",
        src_root / "streamlit_ui" / "components",
        src_root / "streamlit_ui" / "pages",
        src_root / "utils",
        
        # Data directories
        project_root / "data" / "input" / "resumes",
        project_root / "data" / "input" / "job_descriptions",
        project_root / "data" / "output" / "pdfs",
        project_root / "data" / "output" / "reports",
        project_root / "data" / "temp",
        
        # Testing and docs
        project_root / "tests" / "unit",
        project_root / "tests" / "integration", 
        project_root / "tests" / "fixtures",
        project_root / "docs",
        project_root / "logs",
    ]
    
    # Create directories
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        print(f"[CREATED] Directory: {directory}")
    
    # Create __init__.py files for Python packages
    init_files = [
        src_root / "__init__.py",
        src_root / "config" / "__init__.py",
        src_root / "core" / "__init__.py",
        src_root / "core" / "resume_parser" / "__init__.py",
        src_root / "core" / "job_analyzer" / "__init__.py", 
        src_root / "core" / "ai_integration" / "__init__.py",
        src_root / "core" / "ats_optimizer" / "__init__.py",
        src_root / "core" / "pdf_generator" / "__init__.py",
        src_root / "streamlit_ui" / "__init__.py",
        src_root / "streamlit_ui" / "components" / "__init__.py",
        src_root / "streamlit_ui" / "pages" / "__init__.py",
        src_root / "utils" / "__init__.py",
        project_root / "tests" / "__init__.py",
    ]
    
    for init_file in init_files:
        safe_write_text(init_file, '"""Package initialization."""\n', overwrite=False)

def create_project_files(project_root: Path, project_name: str, overwrite: bool = False):
    """Create essential project files."""
    # Core project files
    files = {
        "pyproject.toml": get_pyproject_toml_content(project_name),
        ".env.example": get_env_example_content(),
        ".gitignore": get_gitignore_content(),
        "README.md": get_readme_content(project_name),
        ".python-version": "3.11\n",  # Default Python version
    }
    
    for filename, content in files.items():
        safe_write_text(project_root / filename, content, overwrite=overwrite)

# -------------------------
# Main Setup Workflow 
# -------------------------

def setup_uv_project(assets_dir: Path, project_root: Path, project_name: str, 
                    overwrite: bool = False):
    """Complete uv project setup workflow."""
    
    print(f"[INFO] Setting up uv project: {project_name}")
    print(f"[INFO] Assets source: {assets_dir}")
    print(f"[INFO] Project destination: {project_root}")
    
    # 1. Create project structure
    print("\n[STEP 1] Creating project structure...")
    create_uv_project_structure(project_root, project_name)
    
    # 2. Create core project files
    print("\n[STEP 2] Creating project files...")
    create_project_files(project_root, project_name, overwrite=overwrite)
    
    # 3. Map and copy assets
    print("\n[STEP 3] Mapping exported assets...")
    mappings = get_asset_mappings(assets_dir, project_root, project_name)
    copied_files = []
    
    for mapping in mappings:
        patterns = mapping["patterns"]
        dest = mapping["dest"]
        is_bulk = mapping.get("bulk", False)
        
        if is_bulk:
            # Handle bulk file copying (e.g., data files)
            matches = []
            for pattern in patterns:
                matches.extend(assets_dir.rglob(pattern))
            
            dest.mkdir(parents=True, exist_ok=True)
            for match in matches:
                target = dest / match.name
                if safe_copy(match, target, overwrite=overwrite):
                    copied_files.append(target)
        else:
            # Handle single file mapping
            result = find_and_copy_asset(assets_dir, patterns, dest, overwrite=overwrite)
            if result:
                copied_files.append(result)
    
    print(f"\n[STEP 4] Asset mapping completed - {len(copied_files)} files processed")
    
    return copied_files

def initialize_uv_environment(project_root: Path):
    """Initialize uv environment and install dependencies."""
    print("\n[STEP 5] Initializing uv environment...")
    
    # Check if pyproject.toml exists
    pyproject_file = project_root / "pyproject.toml"
    if not pyproject_file.exists():
        print("[ERROR] pyproject.toml not found")
        return False
    
    try:
        # Create virtual environment and install dependencies
        print("[INFO] Running uv sync to create environment and install dependencies...")
        result = run_uv_command(["uv", "sync"], cwd=project_root)
        
        if result.returncode == 0:
            print("[SUCCESS] Virtual environment created and dependencies installed")
            
            # Install spaCy model
            print("[INFO] Installing spaCy English model...")
            spacy_result = run_uv_command(
                ["uv", "run", "python", "-m", "spacy", "download", "en_core_web_sm"],
                cwd=project_root,
                check=False
            )
            
            if spacy_result.returncode == 0:
                print("[SUCCESS] spaCy model installed")
            else:
                print("[WARNING] spaCy model installation failed - install manually later")
            
            return True
        else:
            print("[ERROR] Failed to setup uv environment")
            print(f"[ERROR] {result.stderr}")
            return False
            
    except Exception as e:
        print(f"[ERROR] Exception during uv setup: {e}")
        return False

def main():
    """Main setup script entry point."""
    parser = argparse.ArgumentParser(
        description="Transform exported-assets into UV-managed Python project",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic setup
  python setup_project_uv.py --assets ./exported-assets
  
  # Custom project name and location
  python setup_project_uv.py --assets ./exported-assets --project-name my-resume-tool --dest ./my-project
  
  # Force overwrite existing files
  python setup_project_uv.py --assets ./exported-assets --force
        """
    )
    
    parser.add_argument(
        "--assets", 
        type=str, 
        default="exported-assets",
        help="Path to exported-assets directory (default: exported-assets)"
    )
    parser.add_argument(
        "--dest",
        type=str, 
        default=".",
        help="Project root destination (default: current directory)"
    )
    parser.add_argument(
        "--project-name",
        type=str,
        default="resume-optimizer", 
        help="Project name (default: resume-optimizer)"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing files"
    )
    parser.add_argument(
        "--no-install",
        action="store_true", 
        help="Skip dependency installation"
    )
    
    args = parser.parse_args()
    
    # Validate inputs
    assets_dir = Path(args.assets).resolve()
    project_root = Path(args.dest).resolve()
    
    if not assets_dir.exists() or not assets_dir.is_dir():
        print(f"[ERROR] Assets directory not found: {assets_dir}")
        sys.exit(1)
    
    # Check UV installation
    if not check_uv_installed():
        sys.exit(1)
    
    # Setup project
    try:
        copied_files = setup_uv_project(
            assets_dir, 
            project_root, 
            args.project_name,
            overwrite=args.force
        )
        
        # Initialize UV environment unless skipped
        if not args.no_install:
            success = initialize_uv_environment(project_root)
            if not success:
                print("[WARNING] Environment setup failed - you can run 'uv sync' manually later")
        
        # Final instructions
        print("\n" + "="*60)
        print("PROJECT SETUP COMPLETED!")
        print("="*60)
        print(f"Project: {project_root}")
        print(f"Copied: {len(copied_files)} files")
        print(f"Dependencies: {'Installed' if not args.no_install else 'Skipped'}")
        
        print("\nNext Steps:")
        print("1. Configure API keys:")
        print("   cp .env.example .env")
        print("   # Edit .env with your Perplexity and Gemini API keys")
        print()
        print("2. Run the application:")
        if args.no_install:
            print("   uv sync  # Install dependencies first")
        normalized_name = args.project_name.lower().replace("-", "_")
        print(f"   uv run streamlit run src/{normalized_name}/streamlit_ui/app.py")
        print()
        print("3. Development commands:")
        print("   uv run pytest           # Run tests")
        print("   uv run black .          # Format code")
        print("   uv add package-name     # Add dependencies")
        print("   uv sync --group dev     # Install dev dependencies")
        
    except KeyboardInterrupt:
        print("\n[INFO] Setup interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n[ERROR] Setup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()