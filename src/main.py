from core.parsing.parser import ResumeParser
from core.services.config_manager import ConfigManager
from core.jobscan.scraper import JobscanScraper
from core.utils import log_helper
from core.utils.helpers import JobParserUtils, ResumeParserUtils
import core.utils.paths as path_utils
from core.services.cv_tailor import TailorAIService
from core.exporting.resume_exporter import ResumeExporter


logger = log_helper.LogHelper(__name__)
config = ConfigManager()
if not path_utils.get_parsed_resume_file_path().is_file():
    resume_parser = ResumeParser(path_utils.get_original_resume_file_path())
    resume = resume_parser.parse()
    resume.write_to_file()
else:
    resume = ResumeParserUtils.parse_resume(path_utils.get_parsed_resume_file_path())
job_details = JobParserUtils.parse_job_details(path_utils.get_job_to_target_file_path())
jobscan_scraper = JobscanScraper(config.settings.jobscan, config.settings.playwright, config.settings.resume, job_details)
match_report, session, match_report_page = jobscan_scraper.run_tailoring(keep_session_open=True) #"Delart_HW Test Automation Engineer/match_report_1.json"

tailor_ai_service = TailorAIService(job_details)
tailored_resume = tailor_ai_service.tailor_cv(resume, match_report.get_keywords_to_prompt())
tailored_resume_json_path = tailored_resume.write_to_json_file(job_details.company, job_details.title)
exporter = ResumeExporter()
tailored_resume_docx_path = exporter.export(tailored_resume, job_details.company, job_details.title)
exporter.docx_to_pdf(tailored_resume_docx_path)

if not match_report.iteration:
    error = "Match reports is missing iteration info"
    logger.error(error)
    raise ValueError(error)
match_report, match_report_page = jobscan_scraper.rescan_resume(session, str(tailored_resume_docx_path), job_details, match_report_page, match_report.iteration + 1)
