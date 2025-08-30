from playwright.sync_api import Page, expect
from core.utils.ui_helpers import PlaywrightHelper
from core.jobscan.pages.match_report_page import MatchReportPage
from core.models.settings import JobscanSettings, ResumeSettings
from core.models.job_to_target import JobDetails


class DashboardPage:
    def __init__(self, page: Page, playwright_helper: PlaywrightHelper, jobscan_settings: JobscanSettings, resume_settings: ResumeSettings):
        self.page = page
        self.jobscan_settings = jobscan_settings
        self.playwright_helper = playwright_helper
        self.resume_settings = resume_settings

        self.resume_text_area = self.page.get_by_placeholder("Paste resume text...")
        self.resume_drag_and_drop_button = self.page.locator("div.resumeActions > label.upload")
        self.resume_upload_input = self.page.locator("div#scanUploader div.inputArea input#file")
        self.job_description_text_area = self.page.locator("textarea#jobDescriptionInput")
        self.scan_button = self.page.locator("//span[normalize-space(.) = 'Scan']/parent::button")

    def upload_resume(self, path_to_resume: str) -> None:
        self.playwright_helper.human_like_mouse_move_and_click(self.page, self.resume_text_area)
        with self.page.expect_file_chooser() as fch:
            self.playwright_helper.delayed_hover_and_click(self.resume_drag_and_drop_button)
            fch.value.set_files(path_to_resume)

    def scan(self, path_to_resume: str, job_details: JobDetails) -> MatchReportPage:
        self.upload_resume(path_to_resume)
        self.playwright_helper.human_like_fill_data(self.page, self.job_description_text_area,  str(job_details))
        expect(self.scan_button).to_be_enabled(timeout=2000)
        self.playwright_helper.human_like_mouse_move_and_click(self.page, self.scan_button)
        self.page.wait_for_url(self.jobscan_settings.match_report_url_pattern, timeout=15000)
        return MatchReportPage(self.page, self.playwright_helper, self.resume_settings, job_details)