from playwright.sync_api import Locator, Page, expect
from core.utils.ui_helpers import PlaywrightHelper
from core.models.settings import ResumeSettings
from core.models.job_to_target import JobDetails


class NewScanComponent:
    def __init__(self, container: Locator, page: Page, playwright_helper: PlaywrightHelper, resume_settings: ResumeSettings) -> None:
        self.container = container
        self.page = page
        self.playwright_helper = playwright_helper
        self.resume_settings = resume_settings

    @property
    def resume_text_area(self) -> Locator:
        return self.container.get_by_placeholder("Paste resume text...")

    @property
    def resume_drag_and_drop_button(self) -> Locator:
        return self.container.locator("div.resumeActions > button.upload")

    @property
    def resume_upload_input(self) -> Locator:
        return self.container.locator("div.inputArea input#file")

    @property
    def job_description_text_area(self) -> Locator:
        return self.container.locator("textarea#jobDescriptionInput")

    @property
    def scan_button(self) -> Locator:
        return self.container.locator("//span[normalize-space(.) = 'Scan']/parent::button")

    @property
    def loading_overlay(self) -> Locator:
        return self.container.locator(".loadingOverlay")

    def upload_resume(self, path_to_resume: str) -> None:
        self.playwright_helper.human_like_mouse_move_and_click(self.page, self.resume_text_area)
        with self.page.expect_file_chooser() as fch:
            self.playwright_helper.delayed_hover_and_click(self.resume_drag_and_drop_button)
            fch.value.set_files(path_to_resume)

    def scan(self, path_to_resume: str, job_details: JobDetails) -> None:
        self.upload_resume(path_to_resume)
        self.playwright_helper.human_like_fill_data(self.page, self.job_description_text_area,  str(job_details))
        expect(self.scan_button).to_be_enabled(timeout=2000)
        self.playwright_helper.human_like_mouse_move_and_click(self.page, self.scan_button)
        self.loading_overlay.wait_for(state="visible", timeout=3000)
        self.loading_overlay.wait_for(state="hidden", timeout=15000)