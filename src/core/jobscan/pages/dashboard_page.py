from playwright.sync_api import Page, expect
from core.utils.ui_helpers import PlaywrightHelper
from core.jobscan.pages.match_report_page import MatchReportPage
from core.models.settings import JobscanSettings, ResumeSettings
from core.models.job_to_target import JobDetails
from core.jobscan.pages.components.new_scan_component import NewScanComponent


class DashboardPage:
    def __init__(self, page: Page, playwright_helper: PlaywrightHelper, jobscan_settings: JobscanSettings, resume_settings: ResumeSettings):
        self.page = page
        self.jobscan_settings = jobscan_settings
        self.playwright_helper = playwright_helper
        self.resume_settings = resume_settings
        self.new_scan_component = NewScanComponent(
            container=self.page.locator("div#scanUploader"),
            page=self.page,
            playwright_helper=self.playwright_helper,
            resume_settings=self.resume_settings)

    def scan(self, path_to_resume: str, job_details: JobDetails) -> MatchReportPage:
        self.new_scan_component.scan(path_to_resume, job_details)
        self.page.wait_for_url(self.jobscan_settings.match_report_url_pattern, timeout=15000)
        return MatchReportPage(page=self.page, playwright_helper=self.playwright_helper, jobscan_settings=self.jobscan_settings, resume_settings=self.resume_settings, job_details=job_details)