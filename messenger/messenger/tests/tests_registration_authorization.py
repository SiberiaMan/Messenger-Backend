from http import HTTPStatus

import pytest
import requests


@pytest.fixture()
def registration_url(base_url):
    return f'{base_url}/v1/registration'


@pytest.fixture()
def authorization_url(base_url):
    return f'{base_url}/v1/authorization'


def test_registration_in_app_repeat_login(registration_url, base_login, base_password):
    headers = {
        "login": base_login,
        "password": base_password
    }
    resp = requests.post(registration_url, headers=headers)
    assert resp.status_code == HTTPStatus.BAD_REQUEST


def test_authorization_valid_login_password(authorization_url, base_login, base_password):
    headers = {
        "login": base_login,
        "password": base_password
    }
    resp = requests.post(authorization_url, headers=headers)
    assert resp.status_code == HTTPStatus.OK
    assert resp.headers.get('session_id')


def test_authorization_invalid_login_password(authorization_url, base_login, base_password):
    headers = {
        "login": "invalid_login",
        "password": 'invalid_password'
    }
    resp = requests.post(authorization_url, headers=headers)
    assert resp.status_code == HTTPStatus.UNAUTHORIZED


def test_authorization_without_login(authorization_url, base_login, base_password):
    headers = {
        "password": base_password
    }
    resp = requests.post(authorization_url, headers=headers)
    assert resp.status_code == HTTPStatus.UNAUTHORIZED


def test_authorization_without_password(authorization_url, base_login, base_password):
    headers = {
        "login": base_login
    }
    resp = requests.post(authorization_url, headers=headers)
    assert resp.status_code == HTTPStatus.UNAUTHORIZED