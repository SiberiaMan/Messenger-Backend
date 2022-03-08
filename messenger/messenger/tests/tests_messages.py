import json
from http import HTTPStatus

import pytest
import requests


@pytest.fixture(scope='session')
def message_create_url(base_url, chat_default_id_messages):
    return f'{base_url}/v1/chats/{chat_default_id_messages}/messages'


@pytest.fixture(scope='session')
def message_get_url(base_url, chat_default_id_messages):
    return f'{base_url}/v1/chats/{chat_default_id_messages}/messages'


@pytest.fixture(scope='session')
def chat_default_id_messages(authorization_headers, base_url):
    chat_create_url = f'{base_url}/v1/chats'
    data = {
        "chat_name": "MSG_CHAT"
    }
    resp = requests.post(chat_create_url, json=data, headers=authorization_headers)
    json_content = json.loads(resp.content)
    chat_id = json_content['chat_id']
    return chat_id


@pytest.fixture(scope='session')
def user_default_id(authorization_headers, base_url, chat_default_id_messages):
    user_create_url = f'{base_url}/v1/chats/{chat_default_id_messages}/users'
    data = {
        "user_name": "dark_killer111"
    }
    resp = requests.post(user_create_url, json=data, headers=authorization_headers)
    json_content = json.loads(resp.content)
    user_id = json_content['user_id']
    return user_id


def test_send_message_unauthorized(message_create_url, user_default_id):
    data = {
        "message": "HELLO WORLD!"
    }
    params = {
        "user_id": str(user_default_id)
    }
    resp = requests.post(message_create_url, json=data, params=params)
    assert resp.status_code == HTTPStatus.UNAUTHORIZED


def test_send_message_invalid_user_id(message_create_url, user_default_id, authorization_headers):
    data = {
        "message": "HELLO WORLD!"
    }
    params = {
        "user_id": str(10101011)
    }
    resp = requests.post(message_create_url, headers=authorization_headers, json=data, params=params)
    assert resp.status_code == HTTPStatus.NOT_FOUND


def test_send_message_invalid_params(message_create_url, user_default_id, authorization_headers):
    data = {
        "wrong_field": "HELLO WORLD!"
    }
    params = {
        "user_id": str(10101011)
    }
    resp = requests.post(message_create_url, headers=authorization_headers, json=data, params=params)
    assert resp.status_code == HTTPStatus.BAD_REQUEST


def test_send_message_created(message_create_url, user_default_id, authorization_headers):
    params = {
        "user_id": str(user_default_id)
    }
    for i in range(10):
        elem = {
            "message": f'hello - {i}'
        }
        resp = requests.post(message_create_url,
                             headers=authorization_headers,
                             json=elem,
                             params=params)
        assert resp.status_code == HTTPStatus.CREATED


@pytest.mark.parametrize(
    "limit",
    [
        None,
        1010299393
    ],
)
def test_get_messages_with_invalid_limit(limit, message_get_url, authorization_headers):
    params = {
        "limit": limit
    }
    resp = requests.get(message_get_url, headers=authorization_headers, params=params)
    assert resp.status_code == HTTPStatus.BAD_REQUEST


@pytest.mark.parametrize(
    "limit",
    [
        1, 5, 10
    ],
)
def test_get_messages_with_valid_limit(limit, message_create_url, authorization_headers):
    limit_params = {"limit": limit}
    resp = requests.get(message_create_url, headers=authorization_headers, params=limit_params)
    assert resp.status_code == HTTPStatus.OK
    messages = json.loads(resp.content)
    assert len(messages['messages']) == limit


@pytest.mark.parametrize(
    "limit, from_",
    [
        (5, 2),
        (10, 2),
        (10, 9)
    ],
)
def test_get_messages_with_limit_offset(limit, from_, message_create_url, authorization_headers):
    params = {"limit": limit, "from": from_}
    resp = requests.get(message_create_url, headers=authorization_headers, params=params)
    assert resp.status_code == HTTPStatus.OK


