import datetime
from _pydatetime import timezone

import pytest
from requests import Session

from db_requester.models import MovieDBModel


class TestMoviesAPI:
    # Тесты для GET /movies
    @pytest.mark.slow
    @pytest.mark.parametrize("min_price,max_price,locations,genre_id", [
        (1, 1000, "MSK", 1),
        (100, 500, "SPB", 2)
    ])
    def test_get_movies(self, common_user, min_price, max_price, locations, genre_id):
        """
        Тест на получение списка фильмов.
        """

        response = common_user.api.movies_api.get_movies(params={
            "locations": locations,
            "minPrice": min_price,
            "maxPrice": max_price,
            "genreId": genre_id
        })
        response_data = response.json()

        movies_list = response_data["movies"]  # Сохраняем полученный список фильмов в переменную

        # Проверки
        assert "movies" in response_data
        assert "count" in response_data
        assert "page" in response_data
        assert "pageSize" in response_data
        assert "pageCount" in response_data
        assert response_data["pageSize"] == 10
        assert movies_list

        for movie in movies_list:
            assert movie["published"] == True

    @pytest.mark.slow
    def test_get_movies_filter_locations(self, common_user):
        """
        Тест на получение списка фильмов только из СПБ используя фильтры.
        """

        response = common_user.api.movies_api.get_movies(params={"locations": "SPB"})
        response_data = response.json()

        movies_list = response_data["movies"] # Сохраняем полученный список фильмов в переменную

        # Проверки
        assert movies_list, "Список фильмов пустой!"

        for movie in movies_list:
            assert movie["location"] == "SPB"

    def test_get_movies_filter_locations_negative(self, common_user):
        """
        Негативный тест на получение списка фильмов только из СПБ используя фильтры.
        """

        response = common_user.api.movies_api.get_movies(params={"locations": "EKB"}, expected_status=400)
        response_data = response.json()

        # Проверки
        assert response_data["message"][0] == "Каждое значение в поле locations должно быть одним из значений: MSK, SPB"


    # Тесты для POST /movies
    def test_create_movie_positive(self, create_test_movie, test_movie, super_admin):
        """
        Позитивный тест создания фильма
        """

        response_data = create_test_movie.json()

        # Проверки
        assert "id" in response_data
        assert response_data["name"] == test_movie["name"]
        assert response_data["price"] == test_movie["price"]
        assert response_data["location"] == test_movie["location"]

        # Удаление созданного фильма
        super_admin.api.movies_api.delete_movie(response_data["id"])

    def test_create_movie_duplicate_negative(self, super_admin, test_movie):
        """
        Негативный тест: создание фильма с дублирующимся названием
        """

        # Создаем первый фильм
        create_response = super_admin.api.movies_api.create_movie(test_movie)
        movie_id = create_response.json()["id"]

        # Пытаемся создать дубликат
        response = super_admin.api.movies_api.create_movie(test_movie, expected_status=409)
        response_data = response.json()

        # Проверки
        assert "message" in response_data
        assert response_data["message"] == "Фильм с таким названием уже существует"

        # Удаление созданного фильма
        super_admin.api.movies_api.delete_movie(movie_id)

    def test_create_movie_missing_required_negative(self, super_admin):
        """
        Негативный тест: отсутствие обязательных полей
        """

        invalid_movie_data = {
            "price": 100,
            "location": "MSK"
        }

        response = super_admin.api.movies_api.create_movie(invalid_movie_data, expected_status=400)
        response_data = response.json()

        # Проверки
        expected_messages = [
            "Поле name должно содержать не менее 3 символов",
            "Поле name должно быть строкой",
            "Поле name не может быть пустым",
            "Поле description должно содержать не менее 5 символов",
            "Поле description должно быть строкой",
            "Поле description не может быть пустым",
            "Поле published должно быть булевым значением",
            "Поле published не может быть пустым",
            "Поле genreId должно быть больше 0",
            "Поле genreId должно быть целым числом",
            "Поле genreId должно быть числом",
            "Поле genreId не может быть пустым"
        ]

        assert sorted(response_data["message"]) == sorted(expected_messages)

    # Тесты для GET /movies/{id}
    @pytest.mark.slow
    def test_get_movie_by_id_positive(self, create_test_movie, common_user, super_admin, test_movie):
        """
        Позитивный тест получения фильма по ID
        """

        # Создаем фильм для теста
        movie_id = create_test_movie.json()["id"]

        # Получаем фильм по ID
        response = common_user.api.movies_api.get_movie_by_id(movie_id)
        response_data = response.json()

        # Проверки
        assert response_data["id"] == movie_id

        # Удаление созданного фильма
        super_admin.api.movies_api.delete_movie(movie_id)

    @pytest.mark.slow
    def test_get_movie_by_id_not_found_negative(self, common_user):
        """
        Негативный тест: получение несуществующего фильма
        """

        non_existent_id = 99999
        response = common_user.api.movies_api.get_movie_by_id(non_existent_id, expected_status=404)
        response_data = response.json()

        # Проверки
        assert "message" in response_data
        assert "не найден" in response_data["message"]

    # Тесты для DELETE /movies/{id}
    def test_delete_movie_positive(self, create_test_movie, test_movie, super_admin, db_session):
        """
        Позитивный тест удаления фильма
        """

        # Создаем фильм для теста
        response = create_test_movie.json()
        movie_id = response["id"]
        movie_name = response["name"]

        # проверяем после вызова api_manager.movies_api.create_movie в базе появился наш фильм
        movies_from_db = db_session.query(MovieDBModel).filter(MovieDBModel.name == movie_name)
        assert movies_from_db.count() == 1, "В базе уже присутствует фильм с таким названием"

        # Удаляем фильм
        super_admin.api.movies_api.delete_movie(movie_id)

        # Проверяем, что фильм удален
        super_admin.api.movies_api.get_movie_by_id(movie_id, expected_status=404)

        # проверяем что в конце тестирования фильма с таким названием действительно нет в базе
        movies_from_db = db_session.query(MovieDBModel).filter(MovieDBModel.name == movie_name)
        assert movies_from_db.count() == 0, "Фильм небыл удален из базы!"

    def test_delete_movie_not_found_negative(self, super_admin):
        """
        Негативный тест: удаление несуществующего фильма
        """

        non_existent_id = 99999
        response = super_admin.api.movies_api.delete_movie(non_existent_id, expected_status=404)
        response_data = response.json()

        # Проверки
        assert "message" in response_data
        assert "не найден" in response_data["message"]

    # Тесты для PATCH /movies/{id}
    def test_update_movie_positive(self, create_test_movie, super_admin, test_movie):
        """
        Позитивный тест обновления фильма
        """

        # Создаем фильм для теста
        movie_id = create_test_movie.json()["id"]

        # Обновляем данные
        update_data = {
            "name": "Обновленное название",
            "price": 400,
            "published": False
        }
        patch_response = super_admin.api.movies_api.update_movie(movie_id, update_data)
        patch_data = patch_response.json()

        # Проверки
        assert patch_data["name"] == update_data["name"]
        assert patch_data["price"] == update_data["price"]
        assert patch_data["published"] == update_data["published"]

        # Удаление созданного фильма
        super_admin.api.movies_api.delete_movie(movie_id)

    def test_update_movie_invalid_data_negative(self, create_test_movie, super_admin, test_movie):
        """
        Негативный тест: обновление с невалидными данными
        """

        # Создаем фильм для теста
        movie_id = create_test_movie.json()["id"]

        # Пытаемся обновить с невалидными данными
        invalid_data = {
            "price": -100,  # Отрицательная цена
            "location": "INVALID"  # Недопустимая локация
        }

        response = super_admin.api.movies_api.update_movie(movie_id, invalid_data, expected_status=400)
        response_data = response.json()

        assert response.status_code == 400
        assert "message" in response_data
        assert "price" in response_data["message"][0].lower()
        assert "location" in response_data["message"][1].lower()

        # Удаление созданного фильма
        super_admin.api.movies_api.delete_movie(movie_id)

    def test_update_movie_not_found_negative(self, super_admin):
        """
        Негативный тест: обновление несуществующего фильма
        """

        non_existent_id = 99999
        update_data = {"name": "Новое название"}

        response = super_admin.api.movies_api.update_movie(non_existent_id, update_data, expected_status=404)
        response_data = response.json()

        assert response.status_code == 404
        assert "message" in response_data
        assert "не найден" in response_data["message"]