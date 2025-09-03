from playwright.sync_api import Page, Locator, TimeoutError as PlaywrightTimeoutError
from time import sleep
import random
from core.models.settings import PlaywrightSettings
from core.utils.log_helper import LogHelper


class PlaywrightHelper:
    logger = LogHelper(__name__)

    def __init__(self, playwright_settings: PlaywrightSettings):
        self.min_delay = playwright_settings.min_delay
        self.max_delay = playwright_settings.max_delay

    def delayed_click(self, element: Locator, max_retries: int = 2) -> None:
        """Click element with basic retry logic."""
        for attempt in range(max_retries):
            try:
                element.click()
                sleep(random.uniform(self.min_delay, self.max_delay))
                return
            except (PlaywrightTimeoutError, Exception) as e:
                PlaywrightHelper.logger.warning(f"Click attempt {attempt + 1} failed")
                if attempt < max_retries - 1:
                    sleep(0.2)
        else:
            PlaywrightHelper.logger.error("Failed to click element after all retries")

    def delayed_hover(self, element: Locator, max_retries: int = 2) -> None:
        """Hover over element with basic retry logic."""
        for attempt in range(max_retries):
            try:
                element.hover()
                sleep(random.uniform(self.min_delay, self.max_delay))
                return
            except (PlaywrightTimeoutError, Exception) as e:
                PlaywrightHelper.logger.warning(f"Hover attempt {attempt + 1} failed")
                if attempt < max_retries - 1:
                    sleep(0.2)
        else:
            PlaywrightHelper.logger.error("Failed to hover over element after all retries")

    def delayed_hover_and_click(self, element: Locator, max_retries: int = 2) -> None:
        """Hover over element and click on it with basic retry logic."""
        self.delayed_hover(element, max_retries)
        self.delayed_click(element, max_retries)

    def human_like_mouse_move(self, page: Page):
        mouse = page.mouse
        start_x, start_y = random.randint(0, 100), random.randint(0, 100)

        mouse.move(start_x, start_y)
        sleep(random.uniform(self.min_delay, self.max_delay))

        for _ in range(random.randint(2, 4)):
            offset_x = random.randint(-30, 30)
            offset_y = random.randint(-30, 30)

            mouse.move(start_x + offset_x, start_y + offset_y, steps=random.randint(4, 7))
            sleep(random.uniform(0.1, 0.3))

    def human_like_mouse_move_to_selector(self, page: Page, target_x: float, target_y: float):
        self.human_like_mouse_move(page)
        page.mouse.move(target_x, target_y, steps=random.randint(8, 12))
        sleep(random.uniform(0.2, 0.4))

    def human_like_mouse_move_and_click(self, page: Page, element: Locator, max_retries: int = 3) -> None:
        """
        Perform human-like mouse movement and click with basic error handling and retry.
        
        Args:
            page: Playwright page object
            element: Element to click
            max_retries: Maximum number of retry attempts
            
        Returns:
            None - Method completes successfully or logs error after retries
        """
        for attempt in range(max_retries):
            try:
                # Get bounding box with basic error handling
                bounding_box = element.bounding_box()
                if not bounding_box:
                    PlaywrightHelper.logger.warning(f"No bounding box (attempt {attempt + 1}/{max_retries})")
                    if attempt < max_retries - 1:
                        sleep(0.2)
                    continue
                
                # Calculate center and perform action
                x = bounding_box["x"] + bounding_box["width"] / 2
                y = bounding_box["y"] + bounding_box["height"] / 2
                
                self.human_like_mouse_move_to_selector(page, x, y)
                self.delayed_hover_and_click(element)
                return
            except (PlaywrightTimeoutError, Exception) as e:
                PlaywrightHelper.logger.warning(f"Attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    sleep(0.2)
        else:
            PlaywrightHelper.logger.error("Failed to perform mouse move and click after all retries")

    def human_like_fill_data(self, page: Page, element: Locator, data: str, max_retries: int = 2) -> None:
        for attempt in range(max_retries):
            try:
                self.human_like_mouse_move_and_click(page, element)
                element.fill(data)
                sleep(random.uniform(self.min_delay, self.max_delay))
                return
            except Exception as e:
                PlaywrightHelper.logger.warning(f"Fill attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    sleep(0.2)
        else:
            PlaywrightHelper.logger.error("Failed to fill data after all retries")

    def exists(self, element: Locator, timeout_ms: int = 5000) -> bool:
        """Check if element exists with basic timeout handling."""
        try:
            # element.wait_for(state="attached", timeout=timeout_ms)
            return element.count() > 0 and element.is_enabled()
        except (PlaywrightTimeoutError, Exception):
            return False