# ds-template

[![CI](https://github.com/joaquim-fps/ds-template/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/joaquim-fps/ds-template/actions/workflows/ci.yml)

A reusable modern data science project template for VS Code.

It includes:

- A reusable data science folder structure
- `uv` for dependency and environment management
- `Ruff` for linting and formatting
- `ty` for type checking
- `pytest` for testing
- `pre-commit` for Git hooks
- `just` for command shortcuts
- An interactive project initializer script

## Project structure

```text
.
├── .github/
│   └── workflows/
│       └── ci.yml
├── .vscode/
│   ├── extensions.json
│   └── settings.json
├── data/
│   ├── raw/
│   ├── interim/
│   ├── processed/
│   └── external/
├── logs/
├── models/
├── notebooks/
├── reports/
│   └── figures/
├── scripts/
│   └── init_project.py
├── src/
│   └── ds_template/
│       ├── __init__.py
│       └── config.py
├── tests/
│   └── test_config.py
├── .editorconfig
├── .env.example
├── .gitattributes
├── .gitignore
├── .pre-commit-config.yaml
├── .python-version
├── justfile
├── pyproject.toml
├── README.md
└── uv.lock
```

## Folder conventions

| Folder | Purpose |
|---|---|
| `data/raw/` | Original, immutable data |
| `data/interim/` | Intermediate transformed data |
| `data/processed/` | Final modeling-ready datasets |
| `data/external/` | Third-party data |
| `logs/` | Local log files from scripts, training runs, and pipelines |
| `notebooks/` | Exploration, experiments, and reports |
| `src/` | Reusable project code |
| `tests/` | Automated tests |
| `models/` | Saved model artifacts |
| `reports/figures/` | Exported charts and figures |

*By default, data and generated artifacts are ignored by Git.*

## Starting a new project

This repository is meant to be used as a GitHub template. **After creating a new repository from this template, clone it locally and then run:**

```bash
just init-project
```

The initializer asks for:

- Project name
- Python package name
- Project description
- Author name
- Author email

It automatically updates:

- `pyproject.toml`
- package folder under `src/`
- test imports
- Ruff first-party import config
- Hatch package config
- `.env.example`
- local `.env`
- `README` references


## Common commands

List available commands:

```bash
just
```

Format code:

```bash
just format
```

Run all checks (formatting, type check, pytests):

```bash
just check
```

Run tests:

```bash
just test
```

Run pre-commit checks:

```bash
just precommit
```

Format, check, stage all files, and commit:

```bash
just commit-all "Your message"
```

Run the same checks as GitHub Actions CI:

```bash
just ci
```

Clean local caches:

```bash
just clean
```


## Checks and automation

This template uses three levels of checks:

| Tooling layer | Command | Purpose |
|---|---|---|
| Local checks | `just check` | Run Ruff, formatting check, ty, and pytest locally |
| Pre-commit | `just precommit` or automatic on `git commit` | Run fast Ruff hooks before commits |
| GitHub Actions CI | automatic on push or pull request | Run the full check suite in a clean environment |

Pre-commit is intentionally lightweight. It runs Ruff linting/fixing and formatting. The full suite runs in `just check` and in **GitHub Actions CI**.

## Data policy

The default `.gitignore` excludes:

```text
data/raw/*
data/interim/*
data/processed/*
data/external/*
models/*
reports/figures/*
```

This keeps large, private, generated, or reproducible files out of Git. Alter the file if needed.

For portfolio projects, prefer one of these approaches:

- document where the raw data comes from;
- provide download instructions;
- include a small public sample only when useful;
- document how to regenerate processed data;
- avoid committing trained model artifacts unless they are small and intentional.

## Environment variables

Use `.env.example` to document expected environment variables.

Create a local `.env` file from it:

```bash
cp .env.example .env
```

The real `.env` file is ignored by Git.

## Adding dependencies

Add normal project dependencies:

```bash
uv add package-name
```

Add development-only dependencies:

```bash
uv add --dev package-name
```
Packages already in dependencies include:  `jupyter`, `pandas`, `numpy`, `matplotlib`, `pyarrow` and `python-dotenv`.
