from enum import Enum
from playwright.sync_api import Page, Locator
from core.models.job_to_target import JobDetails
from core.utils.ui_helpers import PlaywrightHelper


class SearchabilityMetrics(str, Enum):
    ATS_TIPS = "ATS Tip"
    CONTACT_INFORMATION = "Contact Information"
    SUMMARY = "Summary"
    SECTION_HEADINGS = "Section Headings"
    JOB_TITLE_MATCH = "Job Title Match"
    DATE_FORMATTING = "Date Formatting"
    EDUCATION_MATCH = "Education Match"
    FILE_TYPE = "File Type"

class MatchReportPage:
    def __init__(self, page: Page, playwright_helper: PlaywrightHelper) -> None:
        self.page = page
        self.playwright_helper = playwright_helper
        self.match_rate_title = self.page.get_by_role("heading", name="Match Rate")
        self.score = self.page.locator("div#score span.number")
        self.upload_and_rescan_button = self.page.locator("button#upload-and-scan")
        self.match_rate_bars = self.page.locator("div.match-rate-bar")
        # Searchability
        self.searchability_metrics = self.page.locator("div#searchability + div.findingSection div.finding")
        # Hard Skills
        # Soft Skills
        # Recruiter tips
        # Formatting

    def __fix_ats_tips(self, job_details: JobDetails) -> None:
        company_input = self.page.get_by_label("Which company are you applying to?")
        url_input = self.page.get_by_label("What is the url of the job listing?")
        update_details_button = self.page.get_by_role("button", name="Update Details")
        if company_input.get_attribute("value") != job_details.company:
            self.playwright_helper.human_like_fill_data(self.page, company_input, job_details.company)
        if job_details.url and url_input.get_attribute("value") != job_details.url:
            self.playwright_helper.human_like_fill_data(self.page, url_input, job_details.url)
        self.playwright_helper.human_like_mouse_move_and_click(self.page, update_details_button)

    def __fix_job_title_match(self, job_details: JobDetails) -> None:
        job_title_input = self.page.get_by_label("What job title are you applying for?")
        update_details_button = self.page.get_by_role("button", name="Update Details")
        self.playwright_helper.human_like_fill_data(self.page, job_title_input, job_details.company)
        self.playwright_helper.human_like_mouse_move_and_click(self.page, update_details_button)

    def __fix_searchability_metrics(self, metric_name: str, element: Locator, job_details: JobDetails) -> None:
        metric = SearchabilityMetrics(metric_name)
        error_message = f"There is no functionality implemented for {metric.value} within {self.__fix_searchability_metrics.__name__} method"
        self.playwright_helper.human_like_mouse_move_and_click(self.page, element.locator("div.checkWrapper span:has-text('Update')"))
        
        match metric:
            case SearchabilityMetrics.ATS_TIPS:
                self.__fix_ats_tips(job_details)
            case SearchabilityMetrics.CONTACT_INFORMATION | SearchabilityMetrics.SUMMARY | SearchabilityMetrics.SECTION_HEADINGS | SearchabilityMetrics.DATE_FORMATTING | SearchabilityMetrics.EDUCATION_MATCH | SearchabilityMetrics.FILE_TYPE:
                raise NotImplementedError(error_message)
            case SearchabilityMetrics.JOB_TITLE_MATCH:
                self.__fix_job_title_match(job_details)

    def check_and_improve_searchability(self, job_details: JobDetails) -> None:
        for metric in self.searchability_metrics:
            name = metric.locator("div.title")
            icon = metric.locator("div.checkRow > div.checkIcon")
            if "fail" in icon.get_attribute("class"):
                self.__fix_searchability_metrics(name, metric, job_details)

