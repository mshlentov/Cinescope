import pytest
import requests

from api.api_manager import ApiManager
from conftest import api_manager
from constants import BASE_URL, HEADERS, REGISTER_ENDPOINT, LOGIN_ENDPOINT


class TestAuthAPI:
    def test_register_user(self, api_manager: ApiManager, test_user):
        """
        Тест на регистрацию пользователя.
        """
        response = api_manager.auth_api.register_user(test_user)
        response_data = response.json()

        # Проверки
        assert response_data["email"] == test_user["email"], "Email не совпадает"
        assert "id" in response_data, "ID пользователя отсутствует в ответе"
        assert "roles" in response_data, "Роли пользователя отсутствуют в ответе"
        assert "USER" in response_data["roles"], "Роль USER должна быть у пользователя"

    def test_register_and_login_user(self, api_manager: ApiManager, registered_user):
        """
        Тест на регистрацию и авторизацию пользователя.
        """
        login_data = {
            "email": registered_user["email"],
            "password": registered_user["password"]
        }

        response = api_manager.auth_api.login_user(login_data)
        response_data = response.json()

        # Проверки
        assert "accessToken" in response_data, "Токен доступа отсутствует в ответе"
        assert response_data["user"]["email"] == registered_user["email"], "Email не совпадает"

    def test_negative_login_empty(self, requester, api_manager):

        login_data = {}

        # Отправка запроса на авторизацию
        response = api_manager.auth_api.login_user(login_data, expected_status=401)

        # Тело ответа
        response_data = response.json()

        # Проверки
        assert response_data["message"] == "Неверный логин или пароль"

    def test_negative_login_email(self, requester, api_manager):

        login_data = {
            "email": "123@lolipop.com",
            "password": "123"
        }

        # Отправка запроса на авторизацию
        response = api_manager.auth_api.login_user(login_data, expected_status=401)

        # Тело ответа
        response_data = response.json()

        # Проверки
        assert response_data["message"] == "Неверный логин или пароль"

    def test_negative_login_invalid_password(self, registered_user, api_manager):

        # Тестовые данные с неверным паролем
        login_data = {
            "email": registered_user["email"],
            "password": "Неверный пароль"
        }

        # Отправка запроса на авторизацию
        response = api_manager.auth_api.login_user(login_data, expected_status=401)

        # Тело ответа
        response_data = response.json()

        # Проверки
        assert response_data["message"] == "Неверный логин или пароль"










