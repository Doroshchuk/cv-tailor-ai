from playwright.sync_api import sync_playwright, Playwright
import os
import json
from datetime import datetime, timedelta, timezone
from core.models.settings import JobscanSettings


class JobscanScraper:
    def __init__(self, jobscan_settings: JobscanSettings):
        self.jobscan_settings = jobscan_settings

    @staticmethod
    def get_cached_user_agent(playwright: Playwright, path_to_cached_user_agent: str, max_age_days: int) -> str:
        if os.path.exists(path_to_cached_user_agent):
            with open(path_to_cached_user_agent, "r") as file:
                data = json.load(file)
                generaated_at = datetime.fromisoformat(data["generated_at"])
                if datetime.now(timezone.utc) - generaated_at > timedelta(days=max_age_days):
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


    def login(self) -> None:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=False, slow_mo = 500)
            context = browser.new_context(
                storage_state=self.jobscan_settings.storage_state_path,
                user_agent=JobscanScraper.get_cached_user_agent(playwright, self.jobscan_settings.user_agent_cache_path, self.jobscan_settings.user_agent_cache_max_age_days),
                viewport={"width": self.jobscan_settings.viewport_width, "height": self.jobscan_settings.viewport_height},
                permissions=[],
                device_scale_factor=1,
                is_mobile=False,
                has_touch=False,
                locale=self.jobscan_settings.locale,
                timezone_id=self.jobscan_settings.timezone_id
            )
            page = context.new_page()
            page.goto(self.jobscan_settings.home_url)
            page.pause()
            page.wait_for_url(self.jobscan_settings.home_url, timeout=10000)
            browser.close()