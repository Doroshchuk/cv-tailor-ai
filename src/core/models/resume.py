from pathlib import Path
from pydantic import BaseModel, Field
from typing import Dict, List, Literal, Optional
import json
import core.utils.paths as path_utils

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

class ResumeLite(BaseModel):
    professional_summary: ProfessionalSummary
    technical_skills: List[str] = Field(default_factory=list)
    professional_experience_list: List[ProfessionalExperience] = Field(default_factory=list)

    class Config:
        model_config = {"validate_assignment": True}  # validate on assignment

    def write_to_file(self) -> None:
        parsed_resume_file_path = path_utils.get_parsed_resume_file_path()
        parsed_resume_file_path.parent.mkdir(parents=True, exist_ok=True)

        with parsed_resume_file_path.open("w+") as f:
            json.dump(self.model_dump(mode="json"), f)

        print(f"[write_to_file] Wrote resume JSON to: {parsed_resume_file_path} (exists={parsed_resume_file_path.exists()})")

class Resume(ResumeLite):
    header: Header
    education: Education
    professional_development_list: List[str] = Field(default_factory=list)
   
    def get_lite_version(self):
        return ResumeLite(
            professional_summary=self.professional_summary, 
            technical_skills=self.technical_skills, 
            professional_experience_list=self.professional_experience_list
        )

class KeywordCoverage(BaseModel):
    required: int
    achieved: int
    status: Literal['met', 'not met']
    reason: str

    class Config:
        model_config = {"validate_assignment": True}  # validate on assignment

class TailoredResumeLite(ResumeLite):
    adjustment_notes: List[str] = Field(default_factory=list)
    keyword_coverage: Dict[str, KeywordCoverage] = Field(default_factory=dict)

    class Config:
        model_config = {"validate_assignment": True}  # validate on assignment

    def to_full_resume(self, header: Header, education: Education, professional_development_list: list[str]) -> Resume:
        """Recombine with confidential parts to produce the full Resume."""
        return Resume(
            header=header,
            professional_summary=self.professional_summary, 
            technical_skills=self.technical_skills, 
            professional_experience_list=self.professional_experience_list, 
            education=education,
            professional_development_list=professional_development_list
        )

    def write_to_json_file(self, company: str, job_title: str) -> Path:
        tailored_resume_file_path = path_utils.get_tailored_resume_file_path(company, job_title, path_utils.FileFormat.JSON)
        tailored_resume_file_path.parent.mkdir(parents=True, exist_ok=True)

        with tailored_resume_file_path.open("w+") as f:
            json.dump(self.model_dump(mode="json"), f)

        print(f"[write_to_file] Wrote tailored resume JSON to: {tailored_resume_file_path} (exists={tailored_resume_file_path.exists()})")
        return tailored_resume_file_path