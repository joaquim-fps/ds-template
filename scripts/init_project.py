from __future__ import annotations

import argparse
import re
from pathlib import Path

DEFAULT_DESCRIPTION = "A data science project."

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PACKAGE_ROOT = PROJECT_ROOT / "src"


def normalize_project_name(name: str) -> str:
    """Convert a project title into kebab-case for the project name."""
    normalized = re.sub(r"[^a-zA-Z0-9]+", "-", name.strip().lower())
    return normalized.strip("-")


def normalize_package_name(name: str) -> str:
    """Convert a project title into snake_case for the Python package name."""
    normalized = re.sub(r"[^a-zA-Z0-9]+", "_", name.strip().lower())
    normalized = normalized.strip("_")

    if normalized and normalized[0].isdigit():
        normalized = f"project_{normalized}"

    return normalized


def escape_toml_string(value: str) -> str:
    """Escape a string for TOML basic string usage."""
    return value.replace("\\", "\\\\").replace('"', '\\"')


def prompt_required(label: str) -> str:
    """Prompt until a non-empty value is provided."""
    while True:
        value = input(f"{label}: ").strip()

        if value:
            return value

        print(f"{label} is required.")


def prompt_with_default(label: str, default: str) -> str:
    """Prompt for a value, returning the default when the input is empty."""
    suffix = f" [{default}]" if default else ""
    value = input(f"{label}{suffix}: ").strip()
    return value or default


def extract_toml_string(text: str, key: str, default: str = "") -> str:
    """Extract a simple TOML string value."""
    pattern = re.compile(rf'(?m)^{re.escape(key)}\s*=\s*"([^"]*)"')
    match = pattern.search(text)

    if match is None:
        return default

    return match.group(1)


def extract_author(text: str) -> tuple[str, str]:
    """Extract author name and email from a simple PEP 621 authors entry."""
    name_match = re.search(r'authors\s*=\s*\[\{[^}]*name\s*=\s*"([^"]*)"', text)
    email_match = re.search(r'authors\s*=\s*\[\{[^}]*email\s*=\s*"([^"]*)"', text)

    author_name = name_match.group(1) if name_match else ""
    author_email = email_match.group(1) if email_match else ""

    return author_name, author_email


def discover_current_package_name() -> str:
    """Discover the current importable package folder under src."""
    if not PACKAGE_ROOT.exists():
        msg = f"Could not find src directory: {PACKAGE_ROOT}"
        raise FileNotFoundError(msg)

    package_dirs = [
        path
        for path in PACKAGE_ROOT.iterdir()
        if path.is_dir()
        and not path.name.startswith(".")
        and path.name != "__pycache__"
        and (path / "__init__.py").exists()
    ]

    if len(package_dirs) == 1:
        return package_dirs[0].name

    if not package_dirs:
        msg = "Could not find a package folder under src/. Expected one folder with __init__.py."
        raise FileNotFoundError(msg)

    found = ", ".join(path.name for path in package_dirs)
    msg = f"Found multiple package folders under src/: {found}. Keep only one before initializing."
    raise ValueError(msg)


def set_project_string_key(text: str, key: str, value: str) -> str:
    """Set a simple string key in pyproject.toml."""
    escaped_value = escape_toml_string(value)
    new_line = f'{key} = "{escaped_value}"'
    pattern = re.compile(rf'(?m)^{re.escape(key)}\s*=\s*"[^"]*"')

    if pattern.search(text):
        return pattern.sub(new_line, text, count=1)

    project_section = re.search(r"(?m)^\[project\]\s*$", text)

    if project_section is None:
        msg = "Could not find [project] section in pyproject.toml."
        raise ValueError(msg)

    insert_at = project_section.end()
    return f"{text[:insert_at]}\n{new_line}{text[insert_at:]}"


def set_authors(text: str, author_name: str, author_email: str) -> str:
    """Set the PEP 621 authors field in pyproject.toml."""
    author_name = author_name.strip()
    author_email = author_email.strip()

    if not author_name and not author_email:
        return text

    parts = []

    if author_name:
        parts.append(f'name = "{escape_toml_string(author_name)}"')

    if author_email:
        parts.append(f'email = "{escape_toml_string(author_email)}"')

    new_line = f"authors = [{{ {', '.join(parts)} }}]"
    pattern = re.compile(r"(?m)^authors\s*=\s*\[\{.*\}\]\s*$")

    if pattern.search(text):
        return pattern.sub(new_line, text, count=1)

    description_pattern = re.compile(r'(?m)^description\s*=\s*"[^"]*"\s*$')
    description_match = description_pattern.search(text)

    if description_match is not None:
        insert_at = description_match.end()
        return f"{text[:insert_at]}\n{new_line}{text[insert_at:]}"

    project_section = re.search(r"(?m)^\[project\]\s*$", text)

    if project_section is None:
        msg = "Could not find [project] section in pyproject.toml."
        raise ValueError(msg)

    insert_at = project_section.end()
    return f"{text[:insert_at]}\n{new_line}{text[insert_at:]}"


def replace_in_file(path: Path, replacements: dict[str, str]) -> None:
    """Replace old project/package names in a text file."""
    if not path.exists():
        return

    original = path.read_text(encoding="utf-8")
    updated = original

    for old, new in replacements.items():
        if old:
            updated = updated.replace(old, new)

    if updated != original:
        path.write_text(updated, encoding="utf-8")


def update_pyproject(
    *,
    old_project_name: str,
    old_package_name: str,
    new_project_name: str,
    new_package_name: str,
    description: str,
    author_name: str,
    author_email: str,
) -> None:
    """Update pyproject.toml metadata and package references."""
    path = PROJECT_ROOT / "pyproject.toml"
    text = path.read_text(encoding="utf-8")

    replacements = {
        old_project_name: new_project_name,
        old_package_name: new_package_name,
    }

    for old, new in replacements.items():
        if old:
            text = text.replace(old, new)

    text = set_project_string_key(text, "name", new_project_name)
    text = set_project_string_key(text, "description", description)
    text = set_authors(text, author_name, author_email)

    path.write_text(text, encoding="utf-8")


def set_env_var(text: str, key: str, value: str) -> str:
    """Set or append an environment variable assignment."""
    escaped_value = value.replace('"', '\\"')
    new_line = f'{key}="{escaped_value}"'
    pattern = re.compile(rf"(?m)^{re.escape(key)}=.*$")

    if pattern.search(text):
        return pattern.sub(new_line, text, count=1)

    separator = "" if text.endswith("\n") else "\n"
    return f"{text}{separator}{new_line}\n"


def find_env_example() -> Path:
    """Find the environment example file."""
    dot_env_example = PROJECT_ROOT / ".env.example"
    dash_env_example = PROJECT_ROOT / ".env-example"

    if dot_env_example.exists():
        return dot_env_example

    if dash_env_example.exists():
        return dash_env_example

    return dot_env_example


def update_environment_files(old_project_name: str, new_project_name: str) -> None:
    """Update .env.example and create/update local .env."""
    env_example_path = find_env_example()

    if not env_example_path.exists():
        env_example_path.write_text(
            "# Copy this file to .env and fill in project-specific values.\n\n"
            "# Project\n"
            f'PROJECT_NAME="{new_project_name}"\n',
            encoding="utf-8",
        )

    env_example_text = env_example_path.read_text(encoding="utf-8")

    if old_project_name:
        env_example_text = env_example_text.replace(old_project_name, new_project_name)

    env_example_text = set_env_var(env_example_text, "PROJECT_NAME", new_project_name)
    env_example_path.write_text(env_example_text, encoding="utf-8")

    env_path = PROJECT_ROOT / ".env"

    if env_path.exists():
        env_text = env_path.read_text(encoding="utf-8")

        if old_project_name:
            env_text = env_text.replace(old_project_name, new_project_name)
    else:
        env_text = env_example_text

    env_text = set_env_var(env_text, "PROJECT_NAME", new_project_name)
    env_path.write_text(env_text, encoding="utf-8")


def rename_package_folder(old_package_name: str, new_package_name: str) -> None:
    """Rename the package folder under src."""
    old_path = PACKAGE_ROOT / old_package_name
    new_path = PACKAGE_ROOT / new_package_name

    if old_path == new_path:
        return

    if new_path.exists():
        msg = f"Target package folder already exists: {new_path}"
        raise FileExistsError(msg)

    if not old_path.exists():
        msg = f"Expected package folder not found: {old_path}"
        raise FileNotFoundError(msg)

    old_path.rename(new_path)


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Initialize or update a copied data science project.",
    )
    parser.add_argument(
        "project_title",
        nargs="?",
        help='Human-readable project name, for example "Olist Customer Segmentation".',
    )
    parser.add_argument(
        "--package-name",
        help="Optional Python package name. Defaults to a snake_case version of project title.",
    )
    parser.add_argument(
        "--description",
        help="Optional project description.",
    )
    parser.add_argument(
        "--author-name",
        help="Optional author name.",
    )
    parser.add_argument(
        "--author-email",
        help="Optional author email.",
    )
    return parser.parse_args()


def main() -> None:
    """Initialize or update the copied template."""
    args = parse_args()

    pyproject_path = PROJECT_ROOT / "pyproject.toml"
    pyproject_text = pyproject_path.read_text(encoding="utf-8")

    current_project_name = extract_toml_string(
        pyproject_text,
        "name",
        "ds-template",
    )
    current_description = extract_toml_string(
        pyproject_text,
        "description",
        DEFAULT_DESCRIPTION,
    )
    current_author_name, current_author_email = extract_author(pyproject_text)
    current_package_name = discover_current_package_name()

    project_title = args.project_title or prompt_with_default(
        "Project name",
        current_project_name,
    )
    new_project_name = normalize_project_name(project_title)

    default_package_name = normalize_package_name(project_title)
    new_package_name = args.package_name or prompt_with_default(
        "Python package name",
        default_package_name,
    )

    description = args.description or prompt_with_default(
        "Project description",
        current_description,
    )

    author_name = args.author_name
    if author_name is None:
        author_name = prompt_with_default("Author name", current_author_name)

    author_email = args.author_email
    if author_email is None:
        author_email = prompt_with_default("Author email", current_author_email)

    if not new_project_name:
        msg = "Project name cannot be empty."
        raise ValueError(msg)

    if not new_package_name:
        msg = "Package name cannot be empty."
        raise ValueError(msg)

    replacements = {
        current_project_name: new_project_name,
        current_package_name: new_package_name,
    }

    update_pyproject(
        old_project_name=current_project_name,
        old_package_name=current_package_name,
        new_project_name=new_project_name,
        new_package_name=new_package_name,
        description=description,
        author_name=author_name,
        author_email=author_email,
    )

    files_to_update = [
        PROJECT_ROOT / "README.md",
        PROJECT_ROOT / ".env.example",
        PROJECT_ROOT / ".env-example",
        PROJECT_ROOT / ".env",
        PROJECT_ROOT / "tests" / "test_config.py",
    ]

    for path in files_to_update:
        replace_in_file(path, replacements)

    update_environment_files(
        old_project_name=current_project_name,
        new_project_name=new_project_name,
    )
    rename_package_folder(current_package_name, new_package_name)

    print("Project initialized/updated.")
    print(f"Project name: {current_project_name} -> {new_project_name}")
    print(f"Package name: {current_package_name} -> {new_package_name}")
    print(f"Description: {description}")

    if author_name:
        print(f"Author name: {author_name}")

    if author_email:
        print(f"Author email: {author_email}")

    print()
    print("Next steps:")
    print("1. Review pyproject.toml, README.md, and .env.")
    print("2. Run: uv sync")
    print("3. Run: just format")
    print("4. Run: just check")


if __name__ == "__main__":
    main()
