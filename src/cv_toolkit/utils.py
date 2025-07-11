from .enums import ResumeSectionType, HeaderFields, ProfessionalSummaryFields, ProfessionalExperienceFields, EducationFields, ProfessionalDevelopmentFields, TechnicalSkillsFields
from typing import Sequence
import os
import json

class TextUtils:
    @staticmethod
    def safe_split(text_to_split: str, separator: str, max_splits: int = -1) -> list[str]:
        if separator in text_to_split:
            return text_to_split.split(separator, max_splits)
        return [text_to_split]

    @staticmethod
    def clean_text_list(text_list: list[str]) -> list[str]:
        return [text.strip() for text in text_list if text.strip()]

    @staticmethod
    def safe_get_and_strip(list: list[str], index: int, default_value: str = "") -> str:
        try:
            return list[index].strip()
        except IndexError:
            return default_value

class ValidationUtils:
    @staticmethod
    def check_if_section_empty(section_text: list[str], section_type: ResumeSectionType) -> bool:
        if not section_text:
            print(f"Warning: {section_type.value} section is empty")
            return True
        return False

    @staticmethod
    def validate_required_fields(parsed_data: dict, 
    required_fields: Sequence[HeaderFields | ProfessionalSummaryFields | ProfessionalExperienceFields | EducationFields | ProfessionalDevelopmentFields | TechnicalSkillsFields], 
    section_type: ResumeSectionType) -> bool:
        missing_fields = [field for field in required_fields if not parsed_data.get(field)]
        if missing_fields:
            print(f"Warning: Missing required fields: {missing_fields} within {section_type.value} section")
            return False
        return True

class PositionUtils:
    @staticmethod
    def get_supported_positions() -> list[str]:
        positions = []
        script_dir = os.path.dirname(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))
        try:
            with open(os.path.join(script_dir, "configs/positions.json"), "r") as f:
                roles = dict(json.load(f))
                for role in roles:
                    positions.extend(roles[role]["aliases"])
        except FileNotFoundError as e:
            raise FileNotFoundError(f"Positions config file not found: {e}")
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(f"Error parsing positions.config: {e}", e.doc, e.pos)
        return positions

class EnumUtils:
    @staticmethod
    def get_section_type(text: str) -> ResumeSectionType:
        """Map text to ResumeSectionType enum"""
        text_upper = text.strip().upper()
        for section_type in ResumeSectionType:
            if section_type.value == text_upper:
                return section_type
        return ResumeSectionType.HEADER  # default fallback