from http import HTTPStatus

import pytest
import requests


@pytest.fixture()
def ping_db_url(base_url):
    return f'{base_url}/v1/ping_db'


def test_ping_db(ping_db_url, authorization_headers):
    resp = requests.get(ping_db_url, headers=authorization_headers)
    assert resp.status_code == HTTPStatus.OK
