from http import HTTPStatus

import pytest
import requests


@pytest.fixture()
def chat_create_url(base_url):
    return f'{base_url}/v1/chats'


def test_create_chat_unauthorized(chat_create_url):
    data = {
        "chat_name": "chat-1"
    }
    resp = requests.post(chat_create_url, json=data)
    assert resp.status_code == HTTPStatus.UNAUTHORIZED


def test_create_chat(chat_create_url, authorization_headers):
    data = {
        "chat_name": "chat-1"
    }
    resp = requests.post(chat_create_url, json=data, headers=authorization_headers)
    assert resp.status_code == HTTPStatus.CREATED


def test_create_chat_duplicate(chat_create_url, authorization_headers):
    data = {
        "chat_name": "chat-1"
    }
    resp = requests.post(chat_create_url, json=data, headers=authorization_headers)
    assert resp.status_code == HTTPStatus.BAD_REQUEST


def test_create_invalid_chat(chat_create_url, authorization_headers):
    data = {
        "chat": "chat-1"
    }
    resp = requests.post(chat_create_url, json=data, headers=authorization_headers)
    assert resp.status_code == HTTPStatus.BAD_REQUEST
