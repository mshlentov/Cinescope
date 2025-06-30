import pytest

from api.api_manager import ApiManager
from conftest import api_manager
from models.test_pydantic import RegisterUserResponse, AuthResponse


class TestAuthAPI:
    def test_register_user(self, api_manager: ApiManager, test_user):
        """
        Тест на регистрацию пользователя.
        """
        response = api_manager.auth_api.register_user(test_user)
        register_user_response = RegisterUserResponse(**response.json())

        # Проверки
        assert register_user_response.email == test_user["email"], "Email не совпадает"

    def test_register_and_login_user(self, api_manager: ApiManager, registered_user):
        """
        Тест на регистрацию и авторизацию пользователя.
        """
        login_data = {
            "email": registered_user["email"],
            "password": registered_user["password"]
        }

        response = api_manager.auth_api.login_user(login_data)
        login_user_response = AuthResponse(**response.json())

        # Проверки
        assert login_user_response.user.email == login_data["email"]

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










