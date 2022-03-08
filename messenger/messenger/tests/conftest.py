import time

import pytest
import requests

BASE_URL = 'http://127.0.0.1:8000'
BASE_CHAT_ID = 1
BASE_USER_ID = 1
LOGIN = "login"
PASSWORD = "password"


@pytest.fixture(scope='session')
def authorization_headers(base_url, base_login, base_password):
    authorization_url = f'{base_url}/v1/authorization'
    headers = {
        "login": base_login,
        "password": base_password
    }
    resp = requests.post(authorization_url, headers=headers)
    session_id = resp.headers.get('session_id')
    request_headers = {
        "session_id": session_id
    }
    time.sleep(1)
    return request_headers


@pytest.fixture(scope="session")
def base_url():
    return BASE_URL


@pytest.fixture(scope="session")
def base_login():
    return LOGIN


@pytest.fixture(scope="session")
def base_password():
    return PASSWORD

