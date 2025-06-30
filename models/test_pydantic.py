import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator
from constants import Roles


class PydenticUser(BaseModel):  # Создается класс User с помощью BaseModel от pydantic и указывается
    email: str       # что email должно быть строкой
    fullName: str        # полное имя должно быть строкой
    password: str     # поле пароль должно быть строкой
    passwordRepeat: str # поле повторить пароль должно быть строкой
    roles: list[str]  # поле роль должно быть списком
    banned: Optional[bool] = None
    verified: Optional[bool] = None

    # Валидатор для email
    @field_validator('email')
    def email_must_contain_at(cls, value):
        if '@' not in value:
            raise ValueError('Поле email не содержит символ "@"')
        return value

    # Валидатор для пароля
    @field_validator('password')
    def password_min_length(cls, value):
        if len(value) < 8:
            raise ValueError('Поле пароль содержит меньше 8 символов')
        return value

    # Валидатор для ролей
    @field_validator('roles')
    def validate_roles(cls, value):
        valid_roles = {role.value for role in Roles}
        for role in value:
            if role not in valid_roles:
                raise ValueError(f"Недопустимая роль: {role}. Допустимые значения: {', '.join(valid_roles)}")
        return value

class RegisterUserResponse(BaseModel):
    id: str
    email: str = Field(pattern=r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", description="Email пользователя")
    fullName: str = Field(min_length=1, max_length=100, description="Полное имя пользователя")
    verified: bool
    banned: bool
    roles: list[Roles]
    createdAt: str = Field(description="Дата и время создания пользователя в формате ISO 8601")

    @field_validator("createdAt")
    def validate_created_at(cls, value: str) -> str:
        # Валидатор для проверки формата даты и времени (ISO 8601).
        try:
            datetime.datetime.fromisoformat(value)
        except ValueError:
            raise ValueError("Некорректный формат даты и времени. Ожидается формат ISO 8601.")
        return value

class GetUserResponse(BaseModel):
    id: str
    email: str = Field(pattern=r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", description="Email пользователя")
    fullName: str = Field(min_length=1, max_length=100, description="Полное имя пользователя")
    verified: bool
    banned: bool
    roles: list[Roles]
    createdAt: str = Field(description="Дата и время создания пользователя в формате ISO 8601")

    @field_validator("createdAt")
    def validate_created_at(cls, value: str) -> str:
        # Валидатор для проверки формата даты и времени (ISO 8601).
        try:
            datetime.datetime.fromisoformat(value)
        except ValueError:
            raise ValueError("Некорректный формат даты и времени. Ожидается формат ISO 8601.")
        return value

class LoginUserResponse(BaseModel):
    id: UUID
    email: str = Field(pattern=r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", description="Email пользователя")
    fullName: str = Field(min_length=1, max_length=100, description="Полное имя пользователя")
    roles: list[Roles]

class AuthResponse(BaseModel):
    user: LoginUserResponse
    accessToken: str

