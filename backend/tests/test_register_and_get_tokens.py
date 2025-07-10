import pytest
from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework.test import APIClient

from tests.base_test import BaseTest
from tests.utils.user import (
    FIRST_VALID_USER,
    IN_USE_USER_DATA_FOR_REGISTER,
    INVALID_USER_DATA_FOR_LOGIN,
    INVALID_USER_DATA_FOR_REGISTER,
    RESPONSE_SCHEMA_TOKEN,
    SECOND_VALID_USER,
    THIRD_VALID_USER,
    URL_CREATE_USER,
    URL_LOGIN,
    URL_LOGOUT
)

User = get_user_model()


@pytest.mark.django_db(transaction=True)
class TestUserRegistration(BaseTest):

    def test_nodata_signup(self, api_client: APIClient):
        self.url_bad_request_for_invalid_data(
            client=api_client,
            url=URL_LOGIN
        )

    @pytest.mark.parametrize('user_data', INVALID_USER_DATA_FOR_LOGIN)
    def test_invalid_data_signup(self, api_client: APIClient, user_data: dict):
        self.url_bad_request_for_invalid_data(
            client=api_client,
            url=URL_LOGIN,
            data=user_data
        )

    @pytest.mark.parametrize('user_data', INVALID_USER_DATA_FOR_REGISTER)
    def test_without_data_register(
        self, api_client: APIClient, user_data: dict
    ):
        self.url_bad_request_for_invalid_data(
            client=api_client,
            url=URL_CREATE_USER,
            data=user_data
        )

    @pytest.mark.parametrize('user_data', IN_USE_USER_DATA_FOR_REGISTER)
    @pytest.mark.usefixtures('first_user')
    def test_in_use_data_register(
        self, api_client: APIClient, user_data: dict
    ):
        self.url_bad_request_for_invalid_data(
            client=api_client,
            url=URL_CREATE_USER,
            data=user_data
        )

    @pytest.mark.parametrize(
        'user_data', [FIRST_VALID_USER, SECOND_VALID_USER, THIRD_VALID_USER]
    )
    @pytest.mark.usefixtures('all_user')
    def test_signup(self, api_client: APIClient, user_data: dict):

        response: Response = api_client.post(URL_LOGIN, {
            key: value for key, value in user_data.items()
            if key in ('email', 'password')
        })
        self.url_get_resource(
            response=response,
            url=URL_LOGIN,
            response_schema=RESPONSE_SCHEMA_TOKEN
        )

    def test_logout_authorized_client(
        self, first_user_authorized_client: APIClient
    ):
        response: Response = first_user_authorized_client.post(URL_LOGOUT)
        self.url_returns_no_content(
            response=response,
            url=URL_LOGOUT
        )

    def test_logout_unauthorized_client(self, api_client: APIClient):
        self.url_requires_authorization(
            client=api_client,
            url=URL_LOGOUT
        )
