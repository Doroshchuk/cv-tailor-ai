from functools import cached_property
from pydantic import BaseModel
from typing import List
from core.utils.log_helper import LogLevelEnum
from core.utils.normalization_helpers import NormalizationUtils


class ResumeSettings(BaseModel):
    input_path: str
    output_path: str
    supported_formats: List[str]
    file_name: str
    positions_file: str
    whitelisted_hard_skills: List[str]
    whitelisted_soft_skills: List[str]

    @cached_property
    def get_normalized_whitelisted_hard_skills(self) -> list[str]:
        return NormalizationUtils.normalize_values(self.whitelisted_hard_skills)

    @cached_property
    def get_normalized_whitelisted_soft_skills(self) -> list[str]:
        return NormalizationUtils.normalize_values(self.whitelisted_soft_skills)

class JobDetails(BaseModel):
    job_details_file: str

class CvTailorSettings(BaseModel):
    prompt_instructions_file: str

class LoggingSettings(BaseModel):
    level: LogLevelEnum

class ParsingSettings(BaseModel):
    min_header_lines: int
    min_role_lines: int
    header_contact_separator: str
    education_degree_separator: str
    professional_experience_company_location_separator: str
    education_university_country_separator: str

class JobscanSettings(BaseModel):
    home_url: str
    match_report_url_pattern: str
    storage_state_path: str

class PlaywrightSettings(BaseModel):
    user_agent_cache_path: str
    user_agent_cache_max_age_days: int
    locale: str
    timezone_id: str
    viewport_width: int
    viewport_height: int
    min_delay: float
    max_delay: float

class SettingsModel(BaseModel):
    resume: ResumeSettings
    job: JobDetails
    cv_tailor: CvTailorSettings
    logging: LoggingSettings
    parsing: ParsingSettings
    jobscan: JobscanSettings
    playwright: PlaywrightSettings
