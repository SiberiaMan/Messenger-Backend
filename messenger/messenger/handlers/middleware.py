import random
import string

from aiohttp import web
from typing import Callable, Optional

from sqlalchemy import insert, select
from sqlalchemy.exc import IntegrityError, InterfaceError

from messenger.dbmanager.exceptions import NotFoundChatsUsers
from messenger.handlers import responses
from messenger.handlers.responses import (
    service_unavailable, get_not_found, registration_fail, registration_success,
    not_login_or_password, wrong_login_or_password
)
from messenger.utils import logger
from messenger.handlers.exceptions import NotPasswordLogin, WrongLoginPassword, LoginAlreadyTaken
from messenger.db import Login


@logger.logger
async def registration(request: web.Request):
    login = request.headers.get('login')
    password = request.headers.get('password')
    if not login or not password:
        raise NotPasswordLogin('no login' if not login else 'no password')
    async with request.app['db'].begin() as conn:
        await conn.execute(
            insert(Login),
            {"login": login, "password": password})
    return await registration_success()


@logger.logger
async def authorization(request: web.Request):
    """
    является ручкой, до вызова этой ручки вызывается функция ниже, которая создаст session_id
    """
    return web.Response(status=200)


async def authorization_in_middle(request: web.Request) -> Optional[str]:
    login = request.headers.get('login')
    password = request.headers.get('password')
    if not login or not password:
        raise NotPasswordLogin('no login' if not login else 'no password')
    async with request.app['db'].begin() as conn:
        res = await conn.execute(
            select(Login).where(
                Login.login == login, Login.password == password
            ))
        if not res.fetchall():
            raise WrongLoginPassword()
    session_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    request.app['session_login'].set(session_id, login)
    return session_id


async def check_session_id(request: web.Request, session_id: str) -> bool:
    if not request.app['session_login'].get(session_id):
        return False
    return True


async def post_session(request: web.Request, session_id: str):
    login = request.headers.get('login')
    request.app['session_login'].set(session_id, login)


async def create_new_request(request: web.Request, session_id) -> web.Request:
    """
    Если авторизация пользователя прошла успешна, то к этому
    запросу будет добавлен session_id для дальнейшей работы с
    ручками
    """
    headers = request.headers.copy()
    headers['session_id'] = session_id
    new_request = request.clone(
        method=request.method,
        rel_url=request.rel_url,
        headers=headers,
        scheme=request.scheme,
        host=request.host,
        remote=request.remote
    )
    return new_request


async def create_new_response(response: web.Response, session_id: str) -> web.Response:
    """
    Если произошла авторизация перед тем, как дернуть ручку,
    возвращаем в хедере session_id
    """
    headers = response.headers.copy()
    headers['session_id'] = session_id
    response._headers = headers
    return response


@web.middleware
async def middleware(request: web.Request, handler: Callable):
    """
    в мидлваре происходит авторизация пользователей и выдача session_id,
    если прошла авторизация при попытке достучаться до ручки, к ответу
    добавляется session_id
    """
    session_id = None
    reg = request.path.split('/')[-1]
    is_authorized = 0
    try:
        is_session = request.headers.get('session_id')
        alive_session = None
        if is_session:
            alive_session = await check_session_id(request, is_session)
        if (not is_session or not alive_session) and reg != 'registration': #handler.__name__ != 'registration':
            session_id = await authorization_in_middle(request)
            await post_session(request, session_id)
            is_authorized = 1
            request = await create_new_request(request, session_id)
        response = await handler(request)

    except NotPasswordLogin as e:
        return await not_login_or_password(e.text)

    except IntegrityError: # Уникальность логина
        return await registration_fail()

    except WrongLoginPassword:
        return await wrong_login_or_password()

    except (ConnectionRefusedError, InterfaceError):
        return await service_unavailable()

    except web.HTTPError as e:
        return web.Response(body=e.text, status=e.status)

    except NotFoundChatsUsers as e:
        return await get_not_found(e.text)

    except Exception as e:
        print(e)
        await logger.write_log(str(e))
        return await responses.server_error()

    if is_authorized:
        response = await create_new_response(response, session_id)
    return response
