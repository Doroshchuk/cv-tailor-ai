from pydantic import BaseModel
from typing import List
from ..utils.log_helper import LogLevelEnum


class ResumeSettings(BaseModel):
    input_path: str
    output_path: str
    supported_formats: List[str]
    file_name: str

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
    logging: LoggingSettings
    parsing: ParsingSettings
    jobscan: JobscanSettings
    playwright: PlaywrightSettings
