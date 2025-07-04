from playwright.sync_api import Page
from tests.ui.pages.BasePage import BasePage


class DetailsMoviePage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.url = f"{self.home_url}movies/2365"

        # Локаторы элементов
        self.input_review = "textarea[data-qa-id='movie_review_input']"
        self.movie_rating_select = "span[data-qa-id='movie_rating_select']"
        self.rating_select = page.locator('select')
        self.submit_button = "button[data-qa-id='movie_review_submit_button']"


    # Локальные action методы

    def open(self):
        self.open_url(self.url)

    def select_rating(self, value):
        self.rating_select.select_option(value=value, force=True)

    def write_review(self, text):
        self.page.fill(self.input_review, text)

    def submit_click(self):
        self.page.locator(self.submit_button).click()

