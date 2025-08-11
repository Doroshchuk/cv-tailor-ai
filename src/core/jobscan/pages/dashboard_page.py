from playwright.sync_api import Page
from core.utils.ui_helpers import PlaywrightHelper


class DashboardPage:
    def __init__(self, page: Page, playwright_helper: PlaywrightHelper):
        self.page = page
        self.playwright_helper = playwright_helper

        self.resume_text_area = self.page.get_by_placeholder("Paste resume text...")
        self.resume_drag_and_drop_button = self.page.locator("div.resumeActions > label.upload")
        self.resume_upload_input = self.page.locator("div#scanUploader div.inputArea input#file")
        self.job_description_text_area = self.page.locator("textarea#jobDescriptionInput")
        self.scan_button = self.page.get_by_role("button", name="Scan")

    def upload_resume(self, path_to_resume: str):
        self.playwright_helper.human_like_mouse_move_and_click(self.page, self.resume_text_area)
        with self.page.expect_file_chooser() as fch:
            self.playwright_helper.delayed_hover_and_click(self.resume_drag_and_drop_button)
            fch.value.set_files(path_to_resume)


