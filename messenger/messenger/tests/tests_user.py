import json
from http import HTTPStatus

import pytest
import requests


@pytest.fixture(scope='session')
def chat_default_id_users(authorization_headers, base_url):
    chat_create_url = f'{base_url}/v1/chats'
    data = {
        "chat_name": "USER-CHAT"
    }
    resp = requests.post(chat_create_url, json=data, headers=authorization_headers)
    json_content = json.loads(resp.content)
    chat_id = json_content['chat_id']
    return chat_id


@pytest.fixture(scope='session')
def user_create_url(base_url, chat_default_id_users):
    return f'{base_url}/v1/chats/{chat_default_id_users}/users'


def test_create_user_unauthorized(user_create_url):
    data = {
        "user_name": "Mikhail"
    }
    resp = requests.post(user_create_url, json=data)
    assert resp.status_code == HTTPStatus.UNAUTHORIZED


def test_create_user(user_create_url, authorization_headers):
    data = {
        "user_name": "Mikhail"
    }
    resp = requests.post(user_create_url, json=data, headers=authorization_headers)
    assert resp.status_code == HTTPStatus.CREATED


def test_create_repeat_login(user_create_url, authorization_headers):
    data = {
        "user_name": "Ivan"
    }
    resp = requests.post(user_create_url, json=data, headers=authorization_headers)
    assert resp.status_code == HTTPStatus.BAD_REQUEST


def test_create_user_in_invalid_chat(base_url, authorization_headers):
    url = f'{base_url}/chats/2/users'
    data = {
        "user_name": "Mikhail"
    }
    resp = requests.post(url, json=data, headers=authorization_headers)
    assert resp.status_code == HTTPStatus.NOT_FOUND
