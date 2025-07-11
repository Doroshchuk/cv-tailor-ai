from enum import Enum


class ResumeSectionType(str, Enum):
    HEADER = "HEADER",
    PROFESSIONAL_SUMMARY = "PROFESSIONAL SUMMARY",
    TECHNICAL_SKILLS = "TECHNICAL SKILLS",
    PROFESSIONAL_EXPERIENCE = "PROFESSIONAL EXPERIENCE",
    EDUCATION = "EDUCATION",
    PROFESSIONAL_DEVELOPMENT_OR_AFFILIATIONS = "PROFESSIONAL DEVELOPMENT/AFFILIATIONS"

class HeaderFields(str, Enum):
    NAME = "name"
    LOCATION = "location"
    PHONE = "phone"
    EMAIL = "email"
    WORK_AUTHORIZED = "work_authorized"

class ProfessionalSummaryFields(str, Enum):
    SUMMARY = "summary"
    HIGHLIGHTS = "highlights"  

class ProfessionalExperienceFields(str, Enum):
    POSITION = "position"
    DATES = "dates"
    COMPANY = "company"
    LOCATION = "location"
    COMPANY_DESCRIPTION = "company_description"
    PROJECT_DESCRIPTION = "project_description"
    BULLETS = "bullets"

class EducationFields(str, Enum):
    UNIVERSITY = "university"
    COUNTRY = "country"
    DEGREE = "degree"
    FIELD_OF_STUDY = "field_of_study"
    YEAR_OF_GRADUATION = "year_of_graduation"

class ProfessionalDevelopmentFields(str, Enum):
    PROJECTS_OR_CERTIFICATIONS = "projects_or_certifications"

class TechnicalSkillsFields(str, Enum):
    SKILLS = "skills"