import pytest

from models.test_pydantic import RegisterUserResponse, GetUserResponse


class TestUser:

    def test_create_user(self, super_admin, creation_user_data):
        response = RegisterUserResponse(**super_admin.api.user_api.create_user(creation_user_data).json())

        assert response.email == creation_user_data["email"]

    def test_get_user_by_locator(self, super_admin, creation_user_data):
        created_user_response = super_admin.api.user_api.create_user(creation_user_data).json()
        RegisterUserResponse(**created_user_response)

        response_by_id = super_admin.api.user_api.get_user(created_user_response['id']).json()
        GetUserResponse(**response_by_id)

        response_by_email = super_admin.api.user_api.get_user(creation_user_data['email']).json()
        GetUserResponse(**response_by_email)

        assert response_by_id == response_by_email, "Содержание ответов должно быть идентичным"

        assert response_by_id.get('email') == creation_user_data['email']
        assert response_by_id.get('fullName') == creation_user_data['fullName']
        assert response_by_id.get('roles', []) == creation_user_data['roles']
        assert response_by_id.get('verified') is True

    @pytest.mark.slow
    def test_get_user_by_id_common_user(self, common_user):
        common_user.api.user_api.get_user(common_user.email, expected_status=403)