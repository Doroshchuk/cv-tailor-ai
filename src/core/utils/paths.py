from pathlib import Path
from core.services.config_manager import ConfigManager


PROJECT_ROOT = Path(__file__).resolve().parents[2]
CONFIG = ConfigManager()

def get_project_root_path() -> Path:
    """Return the project root directory."""
    return PROJECT_ROOT

def get_configs_dir_path() -> Path:
    """Return the configs directory (version-controlled)."""
    return PROJECT_ROOT / "configs"

def get_jobscan_match_report_path(company: str, job_title: str, iteration: int = 1) -> Path:
    """Return the jobscan match report file path."""
    return (
        Path(get_configs_dir_path())
        / Path(f"{company}_{job_title}")
        / f"match_report_{iteration}.json"
    )

def get_job_to_target_file_path() -> Path:
    """Return the job to target file path."""
    return (
        Path(get_configs_dir_path())
        / CONFIG.settings.job.job_details_file
    )

def get_prompt_instructions_file_path() -> Path:
    """Return the prompt instructions file path."""
    return (
        Path(get_configs_dir_path())
        / CONFIG.settings.cv_tailor.prompt_instructions_file
    )

def get_positions_file_path() -> Path:
    """Return the positions file path."""
    return (
        Path(get_configs_dir_path())
        / CONFIG.settings.resume.positions_file
    )

def get_original_resume_file_path() -> Path:
    """Return the original resume file path."""
    return (
        Path(PROJECT_ROOT)
        / Path(CONFIG.settings.resume.input_path)
        / f"{CONFIG.settings.resume.file_name}.docx"
    )

def get_parsed_resume_file_path() -> Path:
    """Return the parsed resume JSON output file path."""
    return (
        Path(PROJECT_ROOT)
        / Path(CONFIG.settings.resume.output_path)
        / f"{CONFIG.settings.resume.file_name}.json"
    )

def get_tailored_resume_file_path(company: str, job_title: str) -> Path:
    """Return the tailored resume JSON output file path."""
    return (
        Path(get_configs_dir_path())
        / Path(f"{company}_{job_title}")
        / f"tailored_{CONFIG.settings.resume.file_name}.json"
    )