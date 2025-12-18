from core.models.job_to_target import JobDetails
from core.models.prompt_instructions import KeywordStatistics, Prompt
from core.parsing.enums import ResumeSectionType, HeaderFields, ProfessionalSummaryFields, ProfessionalExperienceFields, EducationFields, ProfessionalDevelopmentFields, TechnicalSkillsFields
from typing import Sequence
import json
from pathlib import Path
from core.models.jobscan_match_report import JobscanMatchReport
from core.models.resume import Resume 
from core.utils.log_helper import LogHelper

class TextUtils:
    @staticmethod
    def safe_split(text_to_split: str, separator: str, max_splits: int = -1, logger: LogHelper | None = None) -> list[str]:
        if separator in text_to_split:
            return text_to_split.split(separator, max_splits)
        if logger:
            logger.warning(f"There is no {separator} separator found in {text_to_split}")
        return [text_to_split]

    @staticmethod
    def clean_text_list(text_list: list[str]) -> list[str]:
        return [text.strip() for text in text_list if text.strip()]

    @staticmethod
    def safe_get_and_strip(list: list[str], index: int, default_value: str = "", logger: LogHelper | None = None) -> str:
        try:
            return list[index].strip()
        except IndexError:
            if logger:
                logger.warning(f"Element with {index} index doesn`t exists in {list}")
            return default_value

class ValidationUtils:
    @staticmethod
    def check_if_section_empty(section_text: list[str], section_type: ResumeSectionType, logger: LogHelper | None = None) -> bool:
        if not section_text:
            if logger:
                logger.warning(f"{section_type.value} section is empty")
            return True
        return False

    @staticmethod
    def validate_required_fields(parsed_data: dict, 
    required_fields: Sequence[HeaderFields | ProfessionalSummaryFields | ProfessionalExperienceFields | EducationFields | ProfessionalDevelopmentFields | TechnicalSkillsFields], 
    section_type: ResumeSectionType,
    logger: LogHelper | None = None) -> bool:
        missing_fields = [field for field in required_fields if not parsed_data.get(field)]
        if missing_fields:
            if logger:
                logger.warning(f"Missing required fields: {missing_fields} within {section_type.value} section")
            return False
        return True

class PositionUtils:
    @staticmethod
    def get_supported_positions(path_to_file: Path, logger: LogHelper | None = None) -> list[str]:
        positions = []
        try:
            with path_to_file.open("r") as f:
                roles = dict(json.load(f))
                for role in roles:
                    positions.extend(roles[role]["aliases"])
        except FileNotFoundError as e:
            error_message = f"Positions config file not found: {e}"
            if logger:
                logger.error(error_message)
            raise FileNotFoundError(error_message)
        except json.JSONDecodeError as e:
            error_message = f"Error parsing positions.config: {e}"
            if logger:
                logger.error(error_message)
            raise json.JSONDecodeError(error_message, e.doc, e.pos)
        return positions

class JobParserUtils:
    @staticmethod
    def parse_job_details(path_to_file: Path, logger: LogHelper | None = None) -> JobDetails:
        try:
            with path_to_file.open("r") as f:
                job_details = json.load(f)
        except FileNotFoundError as e:
            error_message = f"Job config file not found: {e}"
            if logger:
                logger.error(error_message)
                raise FileNotFoundError(error_message)
        return JobDetails(**job_details)

class MatchReportParserUtils:
    @staticmethod
    def parse_match_report(path_to_file: Path, logger: LogHelper | None = None) -> JobscanMatchReport:
        try:
            with path_to_file.open("r") as f:
                match_report = json.load(f)
        except FileNotFoundError as e:
            error_message = f"Match Report file not found: {e}"
            if logger:
                logger.error(error_message)
                raise FileNotFoundError(error_message)
        return JobscanMatchReport(**match_report)

class ResumeParserUtils:
    @staticmethod
    def parse_resume(path_to_file: Path, logger: LogHelper | None = None) -> Resume:
        try:
            with path_to_file.open("r") as f:
                resume = json.load(f)
        except FileNotFoundError as e:
            error_message = f"Resume file not found: {e}"
            if logger:
                logger.error(error_message)
                raise FileNotFoundError(error_message)
        return Resume(**resume)

class PromptParserUtils:
    @staticmethod
    def parse_prompt_instructions(path_to_file: Path, logger: LogHelper | None = None) -> Prompt:
        try:
            with path_to_file.open("r") as f:
                prompt = json.load(f)
        except FileNotFoundError as e:
            error_message = f"Prompt Instructions file not found: {e}"
            if logger:
                logger.error(error_message)
                raise FileNotFoundError(error_message)
        return Prompt(**prompt)

class EnumUtils:
    @staticmethod
    def get_section_type(text: str, logger: LogHelper | None = None) -> ResumeSectionType:
        """Map text to ResumeSectionType enum"""
        text_upper = text.strip().upper()
        for section_type in ResumeSectionType:
            if section_type.value == text_upper:
                return section_type
        if logger:
            logger.warning(f"There is no matching for '{text}' in ResumeSectionType enum. Default 'header' is applied instead.")
        return ResumeSectionType.HEADER  # default fallback

class KeywordUtils:
    @staticmethod
    def keywords_to_json(keyword_statistics: KeywordStatistics) -> str:
        return json.dumps(
            {k.value: [kw.model_dump(mode="json") for kw in v] for k, v in keyword_statistics.keywords.items()}
        )