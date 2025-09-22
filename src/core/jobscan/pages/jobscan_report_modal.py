from playwright.sync_api import Page
from core.utils.ui_helpers import PlaywrightHelper


class JobscanReportModal:
    def __init__(self, page: Page, playwright_helper: PlaywrightHelper):
        self.page = page
        self.playwright_helper = playwright_helper
        self.modal = self.page.locator("//div[@role='dialog'][.//h3[normalize-space(.)='Jobscan Report']]")
        self.dismiss_button = self.modal.locator("//button[normalize-space(.)='Dismiss']")

    def is_visible(self, timeout_ms: int = 5000) -> bool:
        try:
            return self.modal.is_visible(timeout=timeout_ms)
        except Exception:
            return False
    
    def dismiss_if_present(self, timeout_ms : int = 5000) -> bool:
        if not self.is_visible(timeout_ms):
            return False
        try:
            self.playwright_helper.human_like_mouse_move_and_click(self.page, self.dismiss_button)
        except Exception:
            self.page.keyboard.press("Escape")

        self.modal.wait_for(state="hidden", timeout=2000)
        return True