from api.api_manager import ApiManager
from conftest import api_manager
from constants import ADMIN_CRED

class TestMoviesAPI:
    def test_get_movies(self, api_manager: ApiManager):
        """
        Тест на получение списка фильмов.
        """

        api_manager.auth_api.authenticate(ADMIN_CRED) # Аунтефикация

        response = api_manager.movies_api.get_all_movies()
        response_data = response.json()

        movies_list = response_data["movies"]  # Сохраняем полученный список фильмов в переменную

        # Проверки
        assert "movies" in response_data
        assert "count" in response_data
        assert "page" in response_data
        assert "pageSize" in response_data
        assert "pageCount" in response_data
        assert response_data["pageSize"] == 10

        if not movies_list:
            raise ValueError("Список фильмов пустой!")
        else:
            for movie in movies_list:
                assert movie["published"] == True

    def test_get_movies_filter_locations(self, api_manager: ApiManager):
        """
        Тест на получение списка фильмов только из СПБ используя фильтры.
        """

        response = api_manager.movies_api.get_movies_filter_locations("SPB")
        response_data = response.json()

        movies_list = response_data["movies"] # Сохраняем полученный список фильмов в переменную

        # Проверки
        if not movies_list:
            raise ValueError("Список фильмов пустой!")
        else:
            for movie in movies_list:
                assert movie["location"] == "SPB"

    def test_get_movies_filter_locations_negative(self, api_manager: ApiManager):
        """
        Тест на получение списка фильмов только из СПБ используя фильтры.
        """

        response = api_manager.movies_api.get_movies_filter_locations("EKB", expected_status=400)
        response_data = response.json()

        # Проверки
        assert response_data["message"][0] == "Каждое значение в поле locations должно быть одним из значений: MSK, SPB"