from core.parsing.parser import ResumeParser
from core.services.config_manager import ConfigManager
from core.jobscan.scraper import JobscanScraper
from core.utils.helpers import JobParserUtils
import core.utils.paths as path_utils


config = ConfigManager()
resume_parser = ResumeParser(path_utils.get_original_resume_file_path())
resume = resume_parser.parse()
resume.write_to_file()
job_details = JobParserUtils.parse_job_details(path_utils.get_job_to_target_file_path())
jobscan_scraper = JobscanScraper(config.settings.jobscan, config.settings.playwright, config.settings.resume, job_details)
jobscan_scraper.run_resume_scan_workflow()