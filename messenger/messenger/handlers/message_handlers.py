from aiohttp import web
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from messenger.db import User
from messenger.dbmanager import (
    connection_manager, disconnection_manager
)
from messenger.handlers.responses import (
    bad_parameters_error, create_response, not_found, response_messages, get_not_found
)

from messenger.utils import logger, validators, message_params
from messenger.handlers.authentication import get_login
from messenger.dbmanager import exceptions


# проверка соединения с бд на ручках, тк надо их логировать

async def check_login_equal_user_id(request: web.Request,
                                    chat: str,
                                    user: str,
                                    login: str):
    """
    Приходит запрос от user_id, надо проверить в юзерах, что логин в сессии и user_id совпадают
    """
    async with request.app['db'].begin() as conn:
        find_login = await conn.execute(
            select(User).where(
                User.id == int(user), User.chat == int(chat), User.login == login
            )
        )
        if not find_login.fetchall():
            raise exceptions.NotFoundChatsUsers('user-not-found')


@logger.logger
async def send_message(request: web.Request):
    chat = request.match_info.get('chat_id')
    user = request.rel_url.query.get('user_id')
    if not chat or not user:
        return await bad_parameters_error()
    try:
        data = await request.text()
        message = validators.SendMessage.parse_raw(data)

        login = await get_login(request)
        await check_login_equal_user_id(request, chat, user, login)

        message_manager = connection_manager.DbMessageManager()
        message_id = await message_manager.post_message(
            chat, user, message.message, engine=request.app['db'], cache=request.app['cache']
        )
    except ValidationError:
        return await bad_parameters_error()
    except IntegrityError as e:
        return await not_found(e)
    except exceptions.NotFoundChatsUsers as e:
        return await get_not_found(e.text)
    return await create_response("message_id", str(message_id))


# здесь DI
@logger.logger
async def get_messages(request: web.Request):
    chat_id = request.match_info.get('chat_id')
    limit = await message_params.get_limit(request)
    if not chat_id or not limit or not 1 <= limit <= 1000:
        return await bad_parameters_error()
    cursor = await message_params.get_cursor(request)  # здесь логика для курсора
    try:
        message_manager = connection_manager.DbMessageManager()
        message, cursor = await message_manager.get_messages(
            limit, cursor, chat_id, request, engine=request.app['db'], cache=request.app['cache']
        )
        return await response_messages(message, cursor, True)
    except ConnectionRefusedError:
        message_manager = disconnection_manager.CacheMessageManager()
        message, cursor = await message_manager.get_messages(
            limit, cursor, chat_id, request, engine=request.app['db'], cache=request.app['cache']
        )
        return await response_messages(message, cursor, False)
    except ValidationError:
        return await bad_parameters_error()
