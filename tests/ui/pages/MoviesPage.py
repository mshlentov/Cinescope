from playwright.sync_api import Page
from tests.ui.pages.BasePage import BasePage


class MoviesPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)

        # Локаторы элементов
        self.details_button = "a[data-qa-id='more_button'][1]"

        # Локальные action методы

    def open_detail_movie(self):
        self.click_element(self.details_button)