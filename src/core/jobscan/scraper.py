from playwright.sync_api import sync_playwright, Playwright
import os
import json
from datetime import datetime, timedelta, timezone
from core.models.settings import JobDetails, JobscanSettings, PlaywrightSettings, ResumeSettings
from core.jobscan.pages.dashboard_page import DashboardPage
from core.utils.ui_helpers import PlaywrightHelper
from core.models.job_to_target import JobDetails


class JobscanScraper:
    def __init__(self, jobscan_settings: JobscanSettings, playwright_settings: PlaywrightSettings, resume_settings: ResumeSettings, job_details: JobDetails):
        self.jobscan_settings = jobscan_settings
        self.playwright_settings = playwright_settings
        self.job_details = job_details
        self.resume_settings = resume_settings
        self.playwright_helper = PlaywrightHelper(self.playwright_settings)
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.abspath(os.path.join(script_dir, "..", ".."))
        self.resume_path = os.path.join(project_root, resume_settings.input_path, f"{resume_settings.file_name}.docx")

    @staticmethod
    def get_cached_user_agent(playwright: Playwright, path_to_cached_user_agent: str, max_age_days: int) -> str:
        if os.path.exists(path_to_cached_user_agent):
            with open(path_to_cached_user_agent, "r") as file:
                data = json.load(file)
                generaated_at = datetime.fromisoformat(data["generated_at"])
                if datetime.now(timezone.utc) - generaated_at <= timedelta(days=max_age_days):
                    return data["user_agent"]
        browser = playwright.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        user_agent = page.evaluate("() => navigator.userAgent")
        browser.close()

        with open(path_to_cached_user_agent, "w") as file:
            json.dump({
                "user_agent": user_agent,
                "generated_at": datetime.now(timezone.utc).isoformat()
            }, file)

        return user_agent


    def run_resume_scan_workflow(self) -> None:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=False)
            context = browser.new_context(
                storage_state=self.jobscan_settings.storage_state_path,
                user_agent=JobscanScraper.get_cached_user_agent(playwright, self.playwright_settings.user_agent_cache_path, self.playwright_settings.user_agent_cache_max_age_days),
                viewport={"width": self.playwright_settings.viewport_width, "height": self.playwright_settings.viewport_height},
                permissions=[],
                device_scale_factor=1,
                is_mobile=False,
                has_touch=False,
                locale=self.playwright_settings.locale,
                timezone_id=self.playwright_settings.timezone_id
            )
            page = context.new_page()
            page.goto(self.jobscan_settings.home_url)
            page.wait_for_url(self.jobscan_settings.home_url, timeout=10000)
            dashboard_page = DashboardPage(page, self.playwright_helper, self.jobscan_settings, self.resume_settings)
            match_report_page = dashboard_page.scan(self.resume_path, str(self.job_details))
            match_report_page.process_match_report(self.job_details)
            browser.close()