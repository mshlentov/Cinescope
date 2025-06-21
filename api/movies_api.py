from custom_requester.custom_requester import CustomRequester
from constants import MOVIES_ENDPOINT

class MoviesAPI(CustomRequester):
    """
    Класс для работы с фильмами.
    """

    def __init__(self, session):
        super().__init__(session=session, base_url="https://api.dev-cinescope.coconutqa.ru/")

    def get_all_movies(self, expected_status=200):
        return self.send_request(
            method="GET",
            endpoint=MOVIES_ENDPOINT,
            expected_status=expected_status
        )

    def get_movies_filter_locations(self, city, expected_status=200):
        return self.send_request(
            method="GET",
            endpoint=f"{MOVIES_ENDPOINT}?locations={city}",
            expected_status=expected_status
        )