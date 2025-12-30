import json
from pathlib import Path
from core.utils.log_helper import LogHelper
from core.parsing.models.job_to_target import JobDetails
from core.jobscan.models.jobscan_match_report import JobscanMatchReport
from core.parsing.models.resume import Resume
from core.services.openai.models.prompt_instructions import Prompt


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