from playwright.sync_api import Page, Locator
from time import sleep
import random
from core.models.settings import PlaywrightSettings


class PlaywrightHelper:
    def __init__(self, playwright_settings: PlaywrightSettings):
        self.min_delay = playwright_settings.min_delay
        self.max_delay = playwright_settings.max_delay

    def delayed_click(self, element: Locator):
        element.click()
        sleep(random.uniform(self.min_delay, self.max_delay))

    def delayed_hover(self, element: Locator):
        element.hover()
        sleep(random.uniform(self.min_delay, self.max_delay))

    def delayed_hover_and_click(self, element: Locator):
        self.delayed_hover(element)
        self.delayed_click(element)

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

    def human_like_mouse_move_and_click(self, page: Page, element: Locator):
        bounding_box = element.bounding_box()
        x = bounding_box["x"] + bounding_box["width"] / 2
        y = bounding_box["y"] + bounding_box["height"] / 2
        self.human_like_mouse_move_to_selector(page, x, y)
        self.delayed_hover_and_click(element)