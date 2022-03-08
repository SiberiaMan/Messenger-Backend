import asyncio

from aiohttp import web
from pydantic import ValidationError
from sqlalchemy import select, insert
from sqlalchemy.exc import IntegrityError, InterfaceError

from messenger.db import Chat, User
from messenger.handlers.responses import (
    db_unavailable, db_available, bad_parameters_error, create_response, not_found, repeat_user, repeat_chat
)
from messenger.dbmanager.exceptions.db_exceptions import RepeatUserInChat
from messenger.utils import logger, validators
from messenger.handlers.authentication import get_login


async def update_chat_users_local(chat_id, login):
    with open('chats-users.txt', 'a+') as fd:
        fd.write(f'{chat_id} {login}\n')


@logger.logger
async def ping_db(request: web.Request):
    try:
        async with request.app['db'].begin() as conn:
            await conn.execute(select(1))
    except (ConnectionRefusedError, InterfaceError):
        return await db_unavailable()
    return await db_available()


@logger.logger
async def chat_create(request: web.Request): # TODO check session
    data = await request.text()
    try:
        chat = validators.CreateChat.parse_raw(data)
        async with request.app['db'].begin() as conn:
            chat_id = await conn.execute(
                insert(Chat, returning=[Chat.id]),
                {"name": chat.chat_name}
            )
            chat_id = chat_id.fetchall()
    except ValidationError:
        return await bad_parameters_error()
    except IntegrityError:
        return await repeat_chat()
    return await create_response("chat_id", str(chat_id[0][0]))  # TODO


async def check_login_in_chat(request: web.Request, chat: str, login: str):
    async with request.app['db'].begin() as conn:
        find_login = await conn.execute(
            select(User).where(
                User.chat == int(chat), User.login == login
            )
        )
    if find_login.fetchall():
        raise RepeatUserInChat()


@logger.logger
async def user_create(request: web.Request):
    chat = request.match_info.get('chat_id')
    if not chat:
        return await bad_parameters_error()
    try:
        data = await request.text()
        user = validators.AddUser.parse_raw(data)
        login = await get_login(request)
        await check_login_in_chat(request, chat, login)
        async with request.app['db'].begin() as conn:
            user_id = await conn.execute(
                insert(User, returning=[User.id]),
                {"name": user.user_name,
                 "chat": int(chat),
                 "login": login}
            )
            user_id = user_id.fetchall()
            await update_chat_users_local(chat, login)
    except IntegrityError as e:
        return await not_found(e)
    except ValidationError:
        return await bad_parameters_error()
    except RepeatUserInChat:
        return await repeat_user()
    except Exception as e:
        print (e)
    return await create_response("user_id", str(user_id[0][0]))
