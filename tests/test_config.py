from pathlib import Path

from ds_template.config import (
    DATA_DIR,
    FIGURES_DIR,
    LOGS_DIR,
    MODELS_DIR,
    PROJECT_ROOT,
    RAW_DATA_DIR,
    REPORTS_DIR,
)


def test_project_root_exists() -> None:
    assert PROJECT_ROOT.exists()
    assert PROJECT_ROOT.is_dir()


def test_project_root_contains_pyproject() -> None:
    assert (PROJECT_ROOT / "pyproject.toml").exists()


def test_data_paths_are_inside_project() -> None:
    assert DATA_DIR == PROJECT_ROOT / "data"
    assert RAW_DATA_DIR == PROJECT_ROOT / "data" / "raw"


def test_artifact_paths_are_inside_project() -> None:
    assert MODELS_DIR == PROJECT_ROOT / "models"
    assert REPORTS_DIR == PROJECT_ROOT / "reports"
    assert FIGURES_DIR == PROJECT_ROOT / "reports" / "figures"
    assert LOGS_DIR == PROJECT_ROOT / "logs"


def test_paths_are_path_objects() -> None:
    assert isinstance(PROJECT_ROOT, Path)
    assert isinstance(DATA_DIR, Path)
