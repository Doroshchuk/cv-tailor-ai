from pathlib import Path
from typing import Optional
from playwright.sync_api import Browser, BrowserContext, sync_playwright, Playwright, TimeoutError as PlaywrightTimeoutError
import os
import json
from datetime import datetime, timedelta, timezone
from core.services.config.models.settings import JobscanSettings, PlaywrightSettings, ResumeSettings
from core.jobscan.pages.dashboard_page import DashboardPage
from core.utils.ui_helpers import PlaywrightHelper
from core.parsing.models.job_to_target import JobDetails
from core.utils.log_helper import LogHelper
from core.jobscan.models.jobscan_match_report import JobscanMatchReport
from core.jobscan.pages.match_report_page import MatchReportPage
from core.jobscan.pages.match_report_page import MatchReportPage
from core.utils.session_helpers import Session
from core.parsing.parsing_utils import MatchReportParserUtils
import core.utils.paths as path_utils


class JobscanScraper:
    logger = LogHelper(__name__)

    def __init__(self, jobscan_settings: JobscanSettings, playwright_settings: PlaywrightSettings, resume_settings: ResumeSettings, job_details: JobDetails):
        self.jobscan_settings = jobscan_settings
        self.playwright_settings = playwright_settings
        self.job_details = job_details
        self.resume_settings = resume_settings
        self.playwright_helper = PlaywrightHelper(self.playwright_settings)
        self.resume_path = path_utils.get_original_resume_file_path()

    @staticmethod
    def get_cached_user_agent(playwright: Playwright, path_to_cached_user_agent: str, max_age_days: int) -> str:
        """
        Get cached user agent or generate a new one with error handling and retry logic.
        Args:
            playwright: Playwright instance
            path_to_cached_user_agent: Path to cache file
            max_age_days: Maximum age of cached user agent in days
        Returns:
            User agent string
        Raises:
            RuntimeError: If unable to generate user agent after retries
        """
        cached_user_agent = JobscanScraper._load_cached_user_agent(path_to_cached_user_agent, max_age_days)
        if cached_user_agent:
            JobscanScraper.logger.info("Using cached user agent")
            return cached_user_agent

        # Generate new user agent with retry logic
        return JobscanScraper._generate_user_agent_with_retry(playwright, path_to_cached_user_agent)

    @staticmethod
    def _load_cached_user_agent(path_to_cached_user_agent: str, max_age_days: int) -> Optional[str]:
        """Load user agent from cache with error handling."""
        try:
            if not os.path.exists(path_to_cached_user_agent):
                JobscanScraper.logger.debug("Cache file does not exist")
                return None
                
            with open(path_to_cached_user_agent, "r") as file:
                data = json.load(file)
                
            # Validate required fields
            if "user_agent" not in data or "generated_at" not in data:
                JobscanScraper.logger.warning("Cache file missing required fields")
                return None
                
            generated_at = datetime.fromisoformat(data["generated_at"])
            if datetime.now(timezone.utc) - generated_at <= timedelta(days=max_age_days):
                JobscanScraper.logger.info("Using valid cached user agent")
                return data["user_agent"]
            else:
                JobscanScraper.logger.info("Cached user agent expired")
                return None
                
        except (FileNotFoundError, PermissionError) as e:
            JobscanScraper.logger.warning(f"Could not read cache file: {e}")
            return None
        except json.JSONDecodeError as e:
            JobscanScraper.logger.warning(f"Invalid JSON in cache file: {e}")
            return None
        except (KeyError, ValueError) as e:
            JobscanScraper.logger.warning(f"Invalid data format in cache file: {e}")
            return None

    @staticmethod
    def _generate_user_agent_with_retry(playwright: Playwright, path_to_cached_user_agent: str, max_retries: int = 3) -> str:
        """Generate user agent with retry logic and error handling."""
        browser = None
        context = None
        
        for attempt in range(max_retries):
            try:
                JobscanScraper.logger.info(f"Generating user agent (attempt {attempt + 1}/{max_retries})")
                
                browser = playwright.chromium.launch(headless=False)
                context = browser.new_context()
                page = context.new_page()
                
                # Add timeout for user agent evaluation
                user_agent = page.evaluate("() => navigator.userAgent")
                
                if not user_agent or len(user_agent.strip()) == 0:
                    raise ValueError("Empty user agent received")
                    
                # Cache the successful result
                JobscanScraper._save_user_agent_to_cache(path_to_cached_user_agent, user_agent)
                JobscanScraper.logger.info("Successfully generated and cached user agent")
                return user_agent
            except (PlaywrightTimeoutError, ValueError) as e:
                JobscanScraper.logger.warning(f"Attempt {attempt + 1} failed: {e}")
                if attempt == max_retries - 1:
                    raise RuntimeError(f"Failed to generate user agent after {max_retries} attempts: {e}")
            except Exception as e:
                JobscanScraper.logger.error(f"Unexpected error during user agent generation: {e}")
                if attempt == max_retries - 1:
                    raise RuntimeError(f"Unexpected error generating user agent: {e}")
            finally:
                # Always cleanup resources
                if context:
                    try:
                        context.close()
                    except Exception as e:
                        JobscanScraper.logger.warning(f"Error closing context: {e}")
                if browser:
                    try:
                        browser.close()
                    except Exception as e:
                        JobscanScraper.logger.warning(f"Error closing browser: {e}")
        else:
            raise RuntimeError("Exhausted retries without valid user agent")

    @staticmethod
    def _save_user_agent_to_cache(path_to_cached_user_agent: str, user_agent: str) -> None:
        """Save user agent to cache with error handling."""
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(path_to_cached_user_agent), exist_ok=True)
            
            with open(path_to_cached_user_agent, "w") as file:
                json.dump({
                    "user_agent": user_agent,
                    "generated_at": datetime.now(timezone.utc).isoformat()
                }, file)
            JobscanScraper.logger.debug("User agent saved to cache")
            
        except (PermissionError, OSError) as e:
            JobscanScraper.logger.warning(f"Could not save user agent to cache: {e}")
            # Don't raise - caching failure shouldn't break the main functionality

    def open_session(self) -> Session:
        self._validate_workflow_inputs()

        pw = sync_playwright().start()
        ua = self.get_cached_user_agent(
            pw,
            self.playwright_settings.user_agent_cache_path,
            self.playwright_settings.user_agent_cache_max_age_days,
        )
        browser = self._launch_browser_with_retry(pw)
        context = self._create_browser_context_with_retry(browser, ua)
        page = context.new_page()
        return Session(pw, browser, context, page)

    def navigate_to_dashboard(self, session: Session) -> None:
        self._navigate_to_dashboard_with_retry(session.page)

    def scan_resume(self, session: Session, path_to_resume: str, iteration: int = 1) -> tuple[JobscanMatchReport, MatchReportPage]:
        """
        Do a fresh scan in the current page/session.
        Returns (report, match_report_page).
        """
        dashboard_page = DashboardPage(page=session.page, playwright_helper=self.playwright_helper, jobscan_settings=self.jobscan_settings, resume_settings=self.resume_settings)
        match_report_page = dashboard_page.scan(path_to_resume, self.job_details)
        report = self._execute_report_processing_workflow(match_report_page, iteration)
        return report, match_report_page

    def rescan_resume(self, session: Session, path_to_resume: str, job_details: JobDetails, match_report_page: MatchReportPage | None, iteration: int) -> tuple[JobscanMatchReport, MatchReportPage]:
        """
        Do rescan in the current page.
        Returns (report, match_report_page).
        """
        if not match_report_page:
            report, match_report_page = self.scan_resume(session, path_to_resume, iteration)
        else:
            match_report_page = match_report_page.rescan(path_to_resume, job_details)
            report = self._execute_report_processing_workflow(match_report_page, iteration=iteration)
        return report, match_report_page

    def run_tailoring(self, existing_match_report_path: Optional[str] = None, keep_session_open: bool = False) -> tuple[JobscanMatchReport, Session, MatchReportPage]:
        match_report_page = None
        session = None
        
        try:
            if existing_match_report_path:
                match_report = MatchReportParserUtils.parse_match_report((
                    Path(path_utils.get_configs_dir_path())
                    / existing_match_report_path
                ))
                if keep_session_open:
                    session = self.open_session()
                    self.navigate_to_dashboard(session)
            else:
                session = self.open_session()
                self.navigate_to_dashboard(session)
                match_report, match_report_page = self.scan_resume(session, self.resume_path)

            return match_report, session, match_report_page

        except Exception as e:
            JobscanScraper.logger.error(f"Tailoring workflow failed: {e}")
            # close session on failure
            if session and not keep_session_open:
                session.close()
            raise
        finally:
            if session and not keep_session_open:
                session.close()

    def _validate_workflow_inputs(self) -> None:
        """Validate all inputs before starting the workflow."""
        # Check if resume file exists
        if not os.path.exists(self.resume_path):
            raise FileNotFoundError(f"Resume file not found: {self.resume_path}")
        
        # Check if storage state file exists
        if not os.path.exists(self.jobscan_settings.storage_state_path):
            JobscanScraper.logger.warning(f"Storage state file not found: {self.jobscan_settings.storage_state_path}")
        
        # Validate settings
        if not self.jobscan_settings.home_url:
            raise ValueError("Home URL is required")
        
        JobscanScraper.logger.info("Workflow inputs validated successfully")
    
    def _launch_browser_with_retry(self, playwright_instance, max_retries: int = 3) -> Browser:
        """Launch browser with retry logic."""
        for attempt in range(max_retries):
            try:
                JobscanScraper.logger.info(f"Launching browser (attempt {attempt + 1}/{max_retries})")
                return playwright_instance.chromium.launch(headless=False)
            except Exception as e:
                JobscanScraper.logger.warning(f"Browser launch attempt {attempt + 1} failed: {e}")
                if attempt == max_retries - 1:
                    raise RuntimeError(f"Failed to launch browser after {max_retries} attempts: {e}")
        else:
            raise RuntimeError("Exhausted retries while trying to launch a browser")

    def _create_browser_context_with_retry(self, browser, user_agent: Optional[str], max_retries: int = 3) -> BrowserContext:
        """Create browser context with retry logic."""
        for attempt in range(max_retries):
            try:
                JobscanScraper.logger.info(f"Creating browser context (attempt {attempt + 1}/{max_retries})")
                
                return browser.new_context(
                    storage_state=self.jobscan_settings.storage_state_path,
                    user_agent=user_agent,
                    viewport={"width": self.playwright_settings.viewport_width, "height": self.playwright_settings.viewport_height},
                    permissions=[],
                    device_scale_factor=1,
                    is_mobile=False,
                    has_touch=False,
                    locale=self.playwright_settings.locale,
                    timezone_id=self.playwright_settings.timezone_id
                )
            except Exception as e:
                JobscanScraper.logger.warning(f"Context creation attempt {attempt + 1} failed: {e}")
                if attempt == max_retries - 1:
                    raise RuntimeError(f"Failed to create browser context after {max_retries} attempts: {e}")
        else:
            raise RuntimeError("Exhausted retries while trying to create browser context")

    def _navigate_to_dashboard_with_retry(self, page, max_retries: int = 3) -> None:
        """Navigate to dashboard with retry logic."""
        for attempt in range(max_retries):
            try:
                JobscanScraper.logger.info(f"Navigating to dashboard (attempt {attempt + 1}/{max_retries})")
                
                page.goto(self.jobscan_settings.home_url, timeout=30000)
                page.wait_for_url(self.jobscan_settings.home_url, timeout=15000)
                
                JobscanScraper.logger.info("Successfully navigated to dashboard")
                return
                
            except PlaywrightTimeoutError as e:
                JobscanScraper.logger.warning(f"Navigation attempt {attempt + 1} timed out: {e}")
                if attempt == max_retries - 1:
                    raise RuntimeError(f"Failed to navigate to dashboard after {max_retries} attempts: {e}")
            except Exception as e:
                JobscanScraper.logger.warning(f"Navigation attempt {attempt + 1} failed: {e}")
                if attempt == max_retries - 1:
                    raise RuntimeError(f"Navigation failed: {e}")
                    
    def _execute_report_processing_workflow(self, match_report_page: MatchReportPage, iteration: int = 1) -> JobscanMatchReport:
        """Execute the scanning workflow with error handling."""
        try:
            report = match_report_page.process_match_report(iteration=iteration)
            
            # Save report with error handling
            try:
                report.write_to_file()
                JobscanScraper.logger.info("Report saved successfully")
            except Exception as e:
                JobscanScraper.logger.warning(f"Failed to save report: {e}")
                # Don't fail the entire workflow if saving fails
            
            return report
            
        except Exception as e:
            JobscanScraper.logger.error(f"Scanning workflow failed: {e}")
            raise RuntimeError(f"Scanning workflow failed: {e}")

    def _cleanup_resources(self, page, context, browser, playwright_instance) -> None:
        """Clean up all resources with error handling."""
        cleanup_order = [page, context, browser, playwright_instance]
        
        for resource in cleanup_order:
            if resource:
                try:
                    if hasattr(resource, 'close'):
                        resource.close()
                    elif hasattr(resource, 'stop'):
                        resource.stop()
                except Exception as e:
                    JobscanScraper.logger.warning(f"Error during resource cleanup: {e}")