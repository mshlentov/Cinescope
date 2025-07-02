import datetime
import os
import uuid

from dotenv import load_dotenv

from faker import Faker
import pytest
import requests

from api.api_manager import ApiManager
from constants import BASE_URL, REGISTER_ENDPOINT, Roles
from custom_requester.custom_requester import CustomRequester
from db_requester.models import UserDBModel
from entities.user import User
from models.test_pydantic import PydenticUser
from resources.user_creds import SuperAdminCreds
from utils.data_generator import DataGenerator
from sqlalchemy import create_engine, Column, String, Boolean, DateTime, text
from sqlalchemy.orm import declarative_base, sessionmaker

faker = Faker()

@pytest.fixture(scope="function")
def test_user():
    """
    Генерация случайного пользователя для тестов.
    """
    random_email = DataGenerator.generate_random_email()
    random_name = DataGenerator.generate_random_name()
    random_password = DataGenerator.generate_random_password()

    user_data = {
        "email": random_email,
        "fullName": random_name,
        "password": random_password,
        "passwordRepeat": random_password,
        "roles": [Roles.USER.value]
    }

    PydenticUser(**user_data)
    return user_data

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
    random_price = DataGenerator.generate_random_price()
    random_location = DataGenerator.generate_random_location()

    return {
        "name": random_name,
        "imageUrl": "https://static.rustore.ru/apk/2063541706/content/ICON/b35776fc-d52d-4294-a521-ac41f44d84bb.png",
        "price": random_price,
        "description": random_desc,
        "location": random_location,
        "published": True,
        "genreId": 2
    }

@pytest.fixture()
def authenticate_admin(api_manager):
    return api_manager.auth_api.authenticate([SuperAdminCreds.USERNAME, SuperAdminCreds.PASSWORD])

@pytest.fixture()
def create_test_movie(test_movie, super_admin):
    yield super_admin.api.movies_api.create_movie(test_movie)

@pytest.fixture
def user_session():
    user_pool = []

    def _create_user_session():
        session = requests.Session()
        user_session = ApiManager(session)
        user_pool.append(user_session)
        return user_session

    yield _create_user_session

    for user in user_pool:
        user.close_session()


@pytest.fixture
def super_admin(user_session):
    new_session = user_session()

    super_admin = User(
        SuperAdminCreds.USERNAME,
        SuperAdminCreds.PASSWORD,
        [Roles.SUPER_ADMIN.value],
        new_session)

    super_admin.api.auth_api.authenticate(super_admin.creds)
    return super_admin

@pytest.fixture(scope="function")
def creation_user_data(test_user):
    updated_data = test_user.copy()
    updated_data.update({
        "verified": True,
        "banned": False
    })
    return updated_data

@pytest.fixture
def common_user(user_session, super_admin, creation_user_data):
    new_session = user_session()

    common_user = User(
        creation_user_data['email'],
        creation_user_data['password'],
        list(Roles.USER.value),
        new_session)

    super_admin.api.user_api.create_user(creation_user_data)
    common_user.api.auth_api.authenticate(common_user.creds)
    return common_user

@pytest.fixture
def registration_user_data():
    random_password = DataGenerator.generate_random_password()

    return {
        "email": DataGenerator.generate_random_email(),
        "fullName": DataGenerator.generate_random_name(),
        "password": random_password,
        "passwordRepeat": random_password,
        "roles": [Roles.USER.value]
    }

USERNAME = os.getenv("DB_USER")
PASSWORD = os.getenv("PASSWORD")
HOST = os.getenv("HOST")
PORT = os.getenv("PORT")
DATABASE_NAME = os.getenv("DATABASE_NAME")

engine = create_engine(f"postgresql+psycopg2://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DATABASE_NAME}") # Создаем движок (engine) для подключения к базе данных
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine) # Создаем фабрику сессий

@pytest.fixture(scope="module")
def db_session():
    """
    Фикстура с областью видимости module.
    Тестовые данные создаются один раз для всех тестов в модуле.
    """
    session = SessionLocal()

    # Создаем тестовые данные
    test_user = UserDBModel(
        id = DataGenerator.generate_random_id(),
        email = DataGenerator.generate_random_email(),
        full_name = DataGenerator.generate_random_name(),
        password = DataGenerator.generate_random_password(),
        created_at = datetime.datetime.now(),
        updated_at = datetime.datetime.now(),
        verified = False,
        banned = False,
        roles = "{USER}"
    )
    session.add(test_user) #добавляем обьект в базу данных
    session.commit() #сохраняем изменения для всех остальных подключений

    yield session # можете запустить тесты в дебаг режиме и поставить тут брекпойнт
                  # зайдите в базу и убедитесь что нывй обьект был создан

	#код ниже выполнится после всех запущеных тестов
    session.delete(test_user) # Удаляем тестовые данные
    session.commit() # сохраняем изменения для всех остальных подключений
    session.close() #завершем сессию (отключаемся от базы данных)