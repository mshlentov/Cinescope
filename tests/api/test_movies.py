from api.api_manager import ApiManager
from conftest import api_manager
from constants import ADMIN_CRED

class TestMoviesAPI:
    # Тесты для GET /movies
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
        api_manager.auth_api.authenticate(ADMIN_CRED)

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
        Негативный тест на получение списка фильмов только из СПБ используя фильтры.
        """
        api_manager.auth_api.authenticate(ADMIN_CRED)

        response = api_manager.movies_api.get_movies_filter_locations("EKB", expected_status=400)
        response_data = response.json()

        # Проверки
        assert response_data["message"][0] == "Каждое значение в поле locations должно быть одним из значений: MSK, SPB"


    # Тесты для POST /movies
    def test_create_movie_positive(self, test_movie, api_manager: ApiManager):
        """
        Позитивный тест создания фильма
        """
        api_manager.auth_api.authenticate(ADMIN_CRED)

        response = api_manager.movies_api.create_movie(test_movie)
        response_data = response.json()

        # Проверки
        assert "id" in response_data
        assert response_data["name"] == test_movie["name"]
        assert response_data["price"] == test_movie["price"]
        assert response_data["location"] == test_movie["location"]

        # Удаление созданного фильма
        api_manager.movies_api.delete_movie(response_data["id"])

    def test_create_movie_duplicate_negative(self, test_movie, api_manager: ApiManager):
        """
        Негативный тест: создание фильма с дублирующимся названием
        """
        api_manager.auth_api.authenticate(ADMIN_CRED)

        # Создаем первый фильм
        create_response = api_manager.movies_api.create_movie(test_movie)
        movie_id = create_response.json()["id"]

        # Пытаемся создать дубликат
        response = api_manager.movies_api.create_movie(test_movie, expected_status=409)
        response_data = response.json()

        # Проверки
        assert "message" in response_data
        assert response_data["message"] == "Фильм с таким названием уже существует"

        # Удаление созданного фильма
        api_manager.movies_api.delete_movie(movie_id)

    def test_create_movie_missing_required_negative(self, api_manager: ApiManager):
        """
        Негативный тест: отсутствие обязательных полей
        """
        api_manager.auth_api.authenticate(ADMIN_CRED)

        invalid_movie_data = {
            "price": 100,
            "location": "MSK"
        }

        response = api_manager.movies_api.create_movie(invalid_movie_data, expected_status=400)
        response_data = response.json()

        # Проверки
        assert response_data["message"] == [
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

    # Тесты для GET /movies/{id}
    def test_get_movie_by_id_positive(self, test_movie, api_manager: ApiManager):
        """
        Позитивный тест получения фильма по ID
        """
        api_manager.auth_api.authenticate(ADMIN_CRED)

        # Создаем фильм для теста
        create_response = api_manager.movies_api.create_movie(test_movie)
        movie_id = create_response.json()["id"]

        # Получаем фильм по ID
        response = api_manager.movies_api.get_movie_by_id(movie_id)
        response_data = response.json()

        # Проверки
        assert response_data["id"] == movie_id

        # Удаление созданного фильма
        api_manager.movies_api.delete_movie(movie_id)

    def test_get_movie_by_id_not_found_negative(self, api_manager: ApiManager):
        """
        Негативный тест: получение несуществующего фильма
        """
        api_manager.auth_api.authenticate(ADMIN_CRED)

        non_existent_id = 99999
        response = api_manager.movies_api.get_movie_by_id(non_existent_id, expected_status=404)
        response_data = response.json()

        # Проверки
        assert "message" in response_data
        assert "не найден" in response_data["message"]

    # Тесты для DELETE /movies/{id}
    def test_delete_movie_positive(self, test_movie, api_manager: ApiManager):
        """
        Позитивный тест удаления фильма
        """
        api_manager.auth_api.authenticate(ADMIN_CRED)

        # Создаем фильм для теста
        create_response = api_manager.movies_api.create_movie(test_movie)
        movie_id = create_response.json()["id"]

        # Удаляем фильм
        delete_response = api_manager.movies_api.delete_movie(movie_id)

        # Проверяем, что фильм удален
        api_manager.movies_api.get_movie_by_id(movie_id, expected_status=404)

    def test_delete_movie_not_found_negative(self, api_manager: ApiManager):
        """
        Негативный тест: удаление несуществующего фильма
        """
        api_manager.auth_api.authenticate(ADMIN_CRED)

        non_existent_id = 99999
        response = api_manager.movies_api.delete_movie(non_existent_id, expected_status=404)
        response_data = response.json()

        # Проверки
        assert "message" in response_data
        assert "не найден" in response_data["message"]

    # Тесты для PATCH /movies/{id}
    def test_update_movie_positive(self, test_movie, api_manager: ApiManager):
        """
        Позитивный тест обновления фильма
        """
        api_manager.auth_api.authenticate(ADMIN_CRED)

        # Создаем фильм для теста
        create_response = api_manager.movies_api.create_movie(test_movie)
        movie_id = create_response.json()["id"]

        # Обновляем данные
        update_data = {
            "name": "Обновленное название",
            "price": 400,
            "published": False
        }
        patch_response = api_manager.movies_api.update_movie(movie_id, update_data)
        patch_data = patch_response.json()

        # Проверки
        assert patch_data["name"] == update_data["name"]
        assert patch_data["price"] == update_data["price"]
        assert patch_data["published"] == update_data["published"]

        # Удаление созданного фильма
        api_manager.movies_api.delete_movie(movie_id)

    def test_update_movie_invalid_data_negative(self, test_movie, api_manager: ApiManager):
        """
        Негативный тест: обновление с невалидными данными
        """
        api_manager.auth_api.authenticate(ADMIN_CRED)

        # Создаем фильм для теста
        create_response = api_manager.movies_api.create_movie(test_movie)
        movie_id = create_response.json()["id"]

        # Пытаемся обновить с невалидными данными
        invalid_data = {
            "price": -100,  # Отрицательная цена
            "location": "INVALID"  # Недопустимая локация
        }

        response = api_manager.movies_api.update_movie(movie_id, invalid_data, expected_status=400)
        response_data = response.json()

        assert response.status_code == 400
        assert "message" in response_data
        assert "price" in response_data["message"][0].lower()
        assert "location" in response_data["message"][1].lower()

        # Удаление созданного фильма
        api_manager.movies_api.delete_movie(movie_id)

    def test_update_movie_not_found_negative(self, api_manager: ApiManager):
        """
        Негативный тест: обновление несуществующего фильма
        """
        api_manager.auth_api.authenticate(ADMIN_CRED)

        non_existent_id = 99999
        update_data = {"name": "Новое название"}

        response = api_manager.movies_api.update_movie(non_existent_id, update_data, expected_status=404)
        response_data = response.json()

        assert response.status_code == 404
        assert "message" in response_data
        assert "не найден" in response_data["message"]