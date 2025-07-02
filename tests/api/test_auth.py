import pytest
from sqlalchemy.orm import Session

from api.api_manager import ApiManager
from conftest import api_manager
from db_requester.models import UserDBModel
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

    def test_register_user_db_session(self, api_manager: ApiManager, test_user, db_session: Session):
        """
        Тест на регистрацию пользователя с проверкой в базе данных.
        """
        # выполняем запрос на регистрацию нового пользователя
        response = api_manager.auth_api.register_user(test_user)
        register_user_response = RegisterUserResponse(**response.json())

        # Проверяем добавил ли сервис Auth нового пользователя в базу данных
        users_from_db = db_session.query(UserDBModel).filter(UserDBModel.id == register_user_response.id)

        # получили обьект из бзы данных и проверили что он действительно существует в единственном экземпляре
        assert users_from_db.count() == 1, "обьект не попал в базу данных"
        # Достаем первый и единственный обьект из списка полученных
        user_from_db = users_from_db.first()
        # можем осуществить проверку всех полей в базе данных например Email
        assert user_from_db.email == register_user_response.email, "Email не совпадает"









