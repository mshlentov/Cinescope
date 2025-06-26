from enum import Enum


class Roles(Enum):
    USER = "USER"
    ADMIN = "ADMIN"
    SUPER_ADMIN = "SUPER_ADMIN"

BASE_URL = "https://auth.dev-cinescope.coconutqa.ru/"
API_URL = "https://api.dev-cinescope.coconutqa.ru/"
HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json"
}

LOGIN_ENDPOINT = "/login"
REGISTER_ENDPOINT = "/register"
MOVIES_ENDPOINT = "/movies"