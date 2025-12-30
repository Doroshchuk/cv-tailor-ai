from __future__ import annotations
from enum import Enum
import time
from playwright.sync_api import Page, Locator
from core.parsing.models.job_to_target import JobDetails
from core.utils.ui_helpers import PlaywrightHelper
from core.jobscan.pages.jobscan_report_modal import JobscanReportModal
from core.jobscan.models.jobscan_match_report import Check, CheckStatusType, JobscanMatchReport, MetricFinding, Skill, SkillType, SkillApplianceType
from core.services.config.models.settings import JobscanSettings, ResumeSettings
from core.jobscan.pages.components.skills_analyzer_component import SkillsAnalyzerComponent
import re
from core.jobscan.pages.components.new_scan_component import NewScanComponent


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
    def __init__(self, page: Page, playwright_helper: PlaywrightHelper, jobscan_settings: JobscanSettings, resume_settings: ResumeSettings, job_details: JobDetails) -> None:
        self.page = page
        self.playwright_helper = playwright_helper
        self.jobscan_settings = jobscan_settings
        self.resume_settings = resume_settings
        self.job_details = job_details
        self.jobscan_report_modal = JobscanReportModal(self.page, self.playwright_helper)
        self.jobscan_match_report = JobscanMatchReport()

        self.title = self.page.locator("//div[normalize-space(.)='Resume scan results']")
        self.scan_sidebar_container = self.page.locator("div.scan-sidebar")
        self.match_rate_title = self.scan_sidebar_container.get_by_role("heading", name="Match Rate")
        self.score = self.scan_sidebar_container.locator("div#score span.number")
        self.upload_and_rescan_button = self.scan_sidebar_container.locator("button#upload-and-scan")
        self.match_rate_bars = self.scan_sidebar_container.locator("div.match-rate-bar")
        # Searchability
        self.searchability_container = self.page.locator("div#searchability")
        self.searchability_metrics = self.page.locator("div#searchability + div.findingSection div.finding")
        # Hard Skills
        self.hard_skills_container = self.page.locator("div#hardSkills + div.skillsAnalyzer")
        # Soft Skills
        self.soft_skills_container = self.page.locator("div#softSkills + div.skillsAnalyzer")
        # Recruiter tips
        self.recruiter_tips_container = self.page.locator("div#recruiterTips")
        self.recruiter_tips_metrics = self.page.locator("div#recruiterTips + div.findingSection div.finding")
        # Formatting
        self.formatting_container = self.page.locator("div#formatting")
        self.formatting_metrics = self.page.locator("div#formatting + div.findingSection div.finding")

        self.new_scan_component = NewScanComponent(
            container=self.page.locator("div.baseModal"),
            page=self.page,
            playwright_helper=self.playwright_helper,
            resume_settings=self.resume_settings)

    def _check_match_rate_bar_for_issues_exist(self, metric_name: str) -> bool:
        title = self.page.locator(f"//div[@class='match-rate-bar']//span[text()='{metric_name}']")
        issues_text = title.locator("//following-sibling::span")
        
        issues_count_match = re.match(r"\d+", issues_text.inner_text())
        if issues_count_match and int(issues_count_match.group()) > 0:
            self.playwright_helper.human_like_mouse_move_and_click(self.page, issues_text)
            return True
        return False

    def _wait_for_match_report_page_to_load(self, timeout_seconds: int = 1) -> None:
        self.title.wait_for(state="visible", timeout=3000)
        self.upload_and_rescan_button.wait_for(state="visible", timeout=3000)
        previous_score = self.score.inner_text()
        while True:
            time.sleep(timeout_seconds)
            if self.score.inner_text() != previous_score:
                previous_score = self.score.inner_text()
            else:
                break

    def process_match_report(self, iteration: int = 1) -> JobscanMatchReport:
        self._wait_for_match_report_page_to_load()
        self.jobscan_report_modal.dismiss_if_present()
        
        jobscan_match_report = JobscanMatchReport(job_title=self.job_details.title, company=self.job_details.company, iteration=iteration, score=int(self.score.inner_text()), report_url=self.page.url)
        jobscan_match_report.metrics.update(self._check_and_process_metric(self.searchability_container, self.searchability_metrics))
        hard_skills: list[Skill] = self._process_skills(SkillType.HARD_SKILL, self.resume_settings.get_normalized_whitelisted_hard_skills)
        soft_skills: list[Skill] = self._process_skills(SkillType.SOFT_SKILL, self.resume_settings.get_normalized_whitelisted_soft_skills)
        sorted_hard_skills: dict[SkillApplianceType, list[Skill]] = {
            SkillApplianceType.APPLIED: [],
            SkillApplianceType.MISSING: []
        }
        sorted_soft_skills: dict[SkillApplianceType, list[Skill]] = {
            SkillApplianceType.APPLIED: [],
            SkillApplianceType.MISSING: []
        }
        for skill in hard_skills:
            sorted_hard_skills[skill.define_appliance_type()].append(skill)
        for skill in soft_skills:
            sorted_soft_skills[skill.define_appliance_type()].append(skill)
        jobscan_match_report.hard_skills = sorted_hard_skills
        jobscan_match_report.soft_skills = sorted_soft_skills
        jobscan_match_report.metrics.update(self._check_and_process_metric(self.recruiter_tips_container, self.recruiter_tips_metrics))
        jobscan_match_report.metrics.update(self._check_and_process_metric(self.formatting_container, self.formatting_metrics))
        return jobscan_match_report

    def _process_skills(self, skill_type: SkillType, whitelisted_skills: list[str]) -> list[Skill]:
        container = self.hard_skills_container if skill_type == SkillType.HARD_SKILL else self.soft_skills_container
        skills_analyzer_component = SkillsAnalyzerComponent(self.page, self.playwright_helper, container, skill_type)
        return skills_analyzer_component.process_skills(whitelisted_skills)

    def _check_and_process_metric(self, container: Locator, findings: Locator) -> dict[str, list[MetricFinding]]:
        metric_title = container.locator("h3").inner_text().split("\n")[0]
        return { metric_title: self._collect_metric_findings(findings) }

    def _get_metric_status(self, element: Locator) -> CheckStatusType:
        class_attr = self.playwright_helper.get_class_attr(element)
        status_value = class_attr.split()[-1] if class_attr else None
        try:
            return CheckStatusType(status_value)
        except ValueError as e:
            raise

    def _collect_metric_findings(self, findings: Locator) -> list[MetricFinding]:
        metric_findings: list[MetricFinding] = []
        for finding in findings.all():
            finding_title = finding.locator("div.title").inner_text()
            checks = finding.locator("div.checkRow").all()
            metric_finding = MetricFinding(title=finding_title)
            is_finding_fully_applied = True
            finding_checks: list[Check] = []

            for check in checks:
                status = self._get_metric_status(check.locator("div.checkIcon"))
                evidence_button = check.locator("div.evidence")
                update_button = check.locator("div.additional span:has-text('Update')")
                details: list[str] = []
                if self.playwright_helper.exists(evidence_button):
                    self.playwright_helper.human_like_mouse_move_and_click(self.page, evidence_button)
                    modal = self.page.locator("div#modal")
                    details.extend(line.strip() for line in modal.inner_text().splitlines() if line)
                    self.playwright_helper.human_like_mouse_move_and_click(self.page, modal.locator("//button[@data-test='dismissableCloseIcon']"))
                elif (status == CheckStatusType.FAIL or status == CheckStatusType.WARN) and self.playwright_helper.exists(update_button) and finding_title != "Job Title Match":
                    self.playwright_helper.human_like_mouse_move_and_click(self.page, update_button)
                    modal = self.page.locator("//div[contains(@class, 'modal')]")
                    modal_title = modal.get_by_role(role="heading").inner_text()
                    if modal_title == "Job Opportunity":
                        self._update_job_opportunity_data(self.job_details)
                        status = self._get_metric_status(check.locator("div.checkIcon"))
                    else:
                        error_message = f"There is no functionality implemented for {modal_title} within {self._collect_metric_findings.__name__} method"
                        raise NotImplementedError(error_message)
                description = check.locator("div.description").inner_text()
                if is_finding_fully_applied and (status == CheckStatusType.FAIL or status == CheckStatusType.WARN):
                    is_finding_fully_applied = False
                finding_checks.append(Check(description=description, details=details, status=status))

            metric_finding.is_fully_applied = is_finding_fully_applied
            metric_finding.checks = finding_checks
            metric_findings.append(metric_finding)

        return metric_findings

    def _update_job_opportunity_data(self, job_details: JobDetails):
        company_input = self.page.get_by_label("Which company are you applying to?")
        job_title_input = self.page.get_by_label("What job title are you applying for?")
        url_input = self.page.get_by_label("What is the url of the job listing?")
        update_details_button = self.page.locator("//button[normalize-space(.)='Update Details']")

        #need to check after rescan - if the values are still missing/incorrect, then it would make sense to depend on the relevant properties from JobscanMatchReport
        if company_input.input_value() != job_details.company:
            self.playwright_helper.human_like_fill_data(self.page, company_input, job_details.company)
        if job_title_input.input_value() != job_details.title:
            self.playwright_helper.human_like_fill_data(self.page, job_title_input, job_details.title)
        if job_details.url and url_input.input_value() != job_details.url:
            self.playwright_helper.human_like_fill_data(self.page, url_input, job_details.url)
        self.playwright_helper.human_like_mouse_move_and_click(self.page, update_details_button)

    def rescan(self, path_to_resume: str, job_details: JobDetails) -> MatchReportPage:
        self.playwright_helper.human_like_mouse_move_and_click(self.page, self.upload_and_rescan_button)
        self.new_scan_component.scan(path_to_resume, job_details)
        self.page.wait_for_url(self.jobscan_settings.match_report_url_pattern, timeout=15000)
        return MatchReportPage(page=self.page, playwright_helper=self.playwright_helper, jobscan_settings=self.jobscan_settings, resume_settings=self.resume_settings, job_details=job_details)