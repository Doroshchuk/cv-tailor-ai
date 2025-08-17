from enum import Enum
from playwright.sync_api import Page, Locator
from core.models.job_to_target import JobDetails
from core.utils.ui_helpers import PlaywrightHelper
from core.jobscan.pages.jobscan_report_modal import JobscanReportModal


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
        self.jobscan_report_modal = JobscanReportModal(self.page, self.playwright_helper)

        self.title = self.page.locator("//div[normalize-space(.)='Resume scan results']")
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

    def __fix_ats_tips(self, metric: Locator, job_details: JobDetails) -> None:
        self.playwright_helper.human_like_mouse_move_and_click(self.page, metric.locator("div.checkWrapper span:has-text('Update')"))
        
        company_input = self.page.get_by_label("Which company are you applying to?")
        url_input = self.page.get_by_label("What is the url of the job listing?")
        update_details_button = self.page.locator("//button[normalize-space(.)='Update Details']")

        if company_input.input_value() != job_details.company:
            self.playwright_helper.human_like_fill_data(self.page, company_input, job_details.company)
        if job_details.url and url_input.input_value() != job_details.url:
            self.playwright_helper.human_like_fill_data(self.page, url_input, job_details.url)
        self.playwright_helper.human_like_mouse_move_and_click(self.page, update_details_button)

    def __fix_job_title_match(self, metric: Locator, job_details: JobDetails) -> None:
        self.playwright_helper.human_like_mouse_move_and_click(self.page, metric.locator("div.checkWrapper span:has-text('Update')"))

        job_title_input = self.page.get_by_label("What job title are you applying for?")
        update_details_button = self.page.locator("//button[normalize-space(.)='Update Details']")

        self.playwright_helper.human_like_fill_data(self.page, job_title_input, job_details.title)
        self.playwright_helper.human_like_mouse_move_and_click(self.page, update_details_button)

    def __fix_searchability_metrics(self, metric_name: str, metric: Locator, job_details: JobDetails) -> None:
        metric_value = SearchabilityMetrics(metric_name)
        error_message = f"There is no functionality implemented for {metric_value.value} within {self.__fix_searchability_metrics.__name__} method"
        
        match metric_value:
            case SearchabilityMetrics.ATS_TIPS:
                self.__fix_ats_tips(metric, job_details)
            case SearchabilityMetrics.CONTACT_INFORMATION | SearchabilityMetrics.SUMMARY | SearchabilityMetrics.SECTION_HEADINGS | SearchabilityMetrics.DATE_FORMATTING | SearchabilityMetrics.EDUCATION_MATCH | SearchabilityMetrics.FILE_TYPE:
                raise NotImplementedError(error_message)
            case SearchabilityMetrics.JOB_TITLE_MATCH:
                self.__fix_job_title_match(metric, job_details)

    def __check_match_rate_bar_for_issues_exist(self, match_rate_bar: Locator) -> bool:
        issues_text = match_rate_bar.locator("div.title > span.text-primary")
        if int(issues_text.inner_text().split(" ")[0]) > 0:
            self.playwright_helper.human_like_mouse_move_and_click(self.page, issues_text)
            return True
        return False

    def check_and_improve_searchability(self, job_details: JobDetails) -> None:
        self.title.wait_for(state="visible", timeout=2000)
        self.jobscan_report_modal.dismiss_if_present()

        searchability_match_bar = self.match_rate_bars.all()[0]
        self.__check_match_rate_bar_for_issues_exist(searchability_match_bar)

        for metric in self.searchability_metrics.all():
            name = metric.locator("div.title").inner_text()
            icons = metric.locator("div.checkRow > div.checkIcon").all()

            if any("fail" in icon.get_attribute("class") for icon in icons) :
                self.__fix_searchability_metrics(name, metric, job_details)