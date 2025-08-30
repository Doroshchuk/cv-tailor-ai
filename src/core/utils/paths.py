from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]

def get_project_root() -> Path:
    """Return the project root directory."""
    return PROJECT_ROOT

def get_configs_dir() -> Path:
    """Return the configs directory (version-controlled)."""
    return PROJECT_ROOT / "configs"