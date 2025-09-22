from core.parsing.parser import ResumeParser
from core.services.config_manager import ConfigManager
from core.jobscan.scraper import JobscanScraper
from core.utils.helpers import JobParserUtils, MatchReportParserUtils, ResumeParserUtils
import core.utils.paths as path_utils
from core.services.cv_tailor import TailorAIService
from pathlib import Path


config = ConfigManager()
if not path_utils.get_parsed_resume_file_path().is_file():
    resume_parser = ResumeParser(path_utils.get_original_resume_file_path())
    resume = resume_parser.parse()
    resume.write_to_file()
else:
    resume = ResumeParserUtils.parse_resume(path_utils.get_parsed_resume_file_path())
job_details = JobParserUtils.parse_job_details(path_utils.get_job_to_target_file_path())
jobscan_scraper = JobscanScraper(config.settings.jobscan, config.settings.playwright, config.settings.resume, job_details)
match_report= jobscan_scraper.run_resume_tailoring_workflow()