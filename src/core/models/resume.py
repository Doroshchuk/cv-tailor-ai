from pydantic import BaseModel, Field
from typing import List, Optional
from pathlib import Path
import json
import core.utils.paths as path_utils
from core.services.config_manager import ConfigManager

class Header(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    linkedin: Optional[str] = None
    github: Optional[str] = None
    work_authorized: Optional[str] = None

    class Config:
        model_config = {"validate_assignment": True}  # validate on assignment

class ProfessionalSummary(BaseModel):
    summary: Optional[str] = None
    highlights: List[str] = Field(default_factory=list)

    class Config:
        model_config = {"validate_assignment": True}  # validate on assignment

class ProfessionalExperience(BaseModel):
    position: Optional[str] = None
    dates: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None
    company_description: Optional[str] = None
    project_description: Optional[str] = None
    bullets: List[str] = Field(default_factory=list)

    class Config:
        model_config = {"validate_assignment": True}  # validate on assignment

class Degree(BaseModel):
    degree: Optional[str] = None
    field_of_study: Optional[str] = None
    year_of_graduation: Optional[str] = None

    class Config:
        model_config = {"validate_assignment": True}  # validate on assignment

class Education(BaseModel):
    university: Optional[str] = None
    country: Optional[str] = None
    degree_list: List[Degree] = Field(default_factory=list)

    class Config:
        model_config = {"validate_assignment": True}  # validate on assignment

class Resume(BaseModel):
    header: Header
    professional_summary: ProfessionalSummary
    technical_skills: List[str] = Field(default_factory=list)
    professional_experience_list: List[ProfessionalExperience] = Field(default_factory=list)
    education: Education
    professional_development_list: List[str] = Field(default_factory=list)

    class Config:
        model_config = {"validate_assignment": True}  # validate on assignment

    def write_to_file(self) -> None:
        parsed_resume_file_path = path_utils.get_parsed_resume_file_path()
        parsed_resume_file_path.parent.mkdir(parents=True, exist_ok=True)

        with parsed_resume_file_path.open("w+") as f:
            json.dump(self.model_dump(mode="json"), f)

        print(f"[write_to_file] Wrote resume JSON to: {parsed_resume_file_path}  (exists={parsed_resume_file_path.exists()})")