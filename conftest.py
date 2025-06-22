
from faker import Faker
import pytest
import requests

from api.api_manager import ApiManager
from constants import BASE_URL, REGISTER_ENDPOINT, LOGIN_ENDPOINT
from custom_requester.custom_requester import CustomRequester
from utils.data_generator import DataGenerator

faker = Faker()

@pytest.fixture(scope="function")
def test_user():
    """
    Генерация случайного пользователя для тестов.
    """
    random_email = DataGenerator.generate_random_email()
    random_name = DataGenerator.generate_random_name()
    random_password = DataGenerator.generate_random_password()

    return {
        "email": random_email,
        "fullName": random_name,
        "password": random_password,
        "passwordRepeat": random_password,
        "roles": ["USER"]
    }

@pytest.fixture(scope="function")
def registered_user(requester, test_user):
    """
    Фикстура для регистрации и получения данных зарегистрированного пользователя.
    """
    response = requester.send_request(
        method="POST",
        endpoint=REGISTER_ENDPOINT,
        data=test_user,
        expected_status=201
    )
    response_data = response.json()
    registered_user = test_user.copy()
    registered_user["id"] = response_data["id"]
    return registered_user

@pytest.fixture(scope="session")
def requester():
    """
    Фикстура для создания экземпляра CustomRequester.
    """
    session = requests.Session()
    return CustomRequester(session=session, base_url=BASE_URL)


@pytest.fixture(scope="session")
def session():
    """
    Фикстура для создания HTTP-сессии.
    """
    http_session = requests.Session()
    http_session.base_url = BASE_URL  # Импортируйте BASE_URL из constants
    yield http_session
    http_session.close()

@pytest.fixture(scope="session")
def api_manager(session):
    """
    Фикстура для создания экземпляра ApiManager.
    """
    return ApiManager(session)

@pytest.fixture(scope="session")
def test_movie():
    """
    Генерация случайного фильма для тестов.
    """
    random_name = DataGenerator.generate_random_movie_name()
    random_desc = DataGenerator.generate_random_movie_name()

    return {
        "name": random_name,
        "imageUrl": "https://static.rustore.ru/apk/2063541706/content/ICON/b35776fc-d52d-4294-a521-ac41f44d84bb.png",
        "price": 200,
        "description": random_desc,
        "location": "SPB",
        "published": True,
        "genreId": 2
    }