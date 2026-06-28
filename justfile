set shell := ["powershell.exe", "-NoLogo", "-Command"]

# List available commands
default:
    just --list

# Initialize a copied template for a new project
init-project:
    uv run python scripts/init_project.py
    uv sync
    uv run ruff format .
    just check

# Run Ruff linting
lint:
    uv run ruff check .

# Run Ruff formatting
format:
    uv run ruff format .

# Check formatting without changing files
format-check:
    uv run ruff format --check .

# Run type checking
typecheck:
    uv run ty check

# Run tests
test:
    uv run pytest

# Run all main checks
check:
    uv run ruff check .
    uv run ruff format --check .
    uv run ty check
    uv run pytest

# Run pre-commit on all files
precommit:
    uv run pre-commit run --all-files

# Format, check, stage all files, and commit with a message
commit-all message:
    just format
    just check
    git add .
    git commit -m "{{message}}"

ci:
    uv sync --locked --all-groups
    uv run ruff check .
    uv run ruff format --check .
    uv run ty check
    uv run pytest

# Clean common local caches
clean:
    python -c "import shutil, pathlib; [shutil.rmtree(p, ignore_errors=True) for p in pathlib.Path('.').rglob('__pycache__')]"
    python -c "import shutil; [shutil.rmtree(p, ignore_errors=True) for p in ['.pytest_cache', '.ruff_cache', '.ty']]"