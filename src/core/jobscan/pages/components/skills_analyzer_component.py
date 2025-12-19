from playwright.sync_api import Page, Locator
from core.jobscan.models.jobscan_match_report import SkillType, SkillApplianceType, Skill
from core.utils.ui_helpers import PlaywrightHelper


class SkillsAnalyzerComponent:
    def __init__(self, page: Page, playwright_helper: PlaywrightHelper, container: Locator, skill_type: SkillType) -> None:
        self.page = page
        self.playwright_helper = playwright_helper
        self.container = container
        self.skill_type = skill_type
    
    @property
    def show_more_button(self) -> Locator:
        return self.container.locator("//button[normalize-space(.)='Show more']")
    
    @property
    def name_columns(self) -> Locator:
        return self.container.locator("span.name")

    @property
    def matching_count_columns(self) -> Locator:
        return self.container.locator("span.count")

    @property
    def required_count_columns(self) -> Locator:
        return self.matching_count_columns.locator("//parent::div/following-sibling::div[1]")

    def process_skills(self, whitelisted_skills: list[str]) -> list[Skill]:
        if self.playwright_helper.exists(self.show_more_button):
            self.playwright_helper.human_like_mouse_move_and_click(self.page, self.show_more_button)
        
        skills: list[Skill] = []
        skill_name_colum_texts = self.name_columns.all_inner_texts()
        skill_matching_count_colum_texts = self.matching_count_columns.all_inner_texts()
        skill_required_column_column_texts = self.required_count_columns.all_inner_texts()
        for i in range(len(skill_name_colum_texts)):
            skill_name = skill_name_colum_texts[i]
            skill_matching_count = 0
            if not self.playwright_helper.exists(self.matching_count_columns.nth(i).locator("span.x")):
                skill_matching_count = int(skill_matching_count_colum_texts[i])
            skill_required_count = int(skill_required_column_column_texts[i].split()[0])
            skill = Skill(name=skill_name, type=self.skill_type, required_quantity=skill_required_count, actual_quantity=skill_matching_count)
            skill.update_is_supported(whitelisted_skills)
            skills.append(skill)

        return skills