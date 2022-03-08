from typing import Optional, Tuple
from aiohttp import web

from sqlalchemy import insert, select
from messenger.dbmanager.exceptions import NotFoundChatsUsers
from messenger.cache import ApiCache
from messenger.dbmanager.base import BaseMessageManager
from sqlalchemy.ext.asyncio import AsyncEngine
from messenger.db import Message, User
from messenger.handlers import authentication


async def get_messages_from_db(chat_id: str,
                               cursor: int,
                               limit: int,
                               engine: AsyncEngine
                               ) -> Tuple[list, str]:
    async with engine.begin() as conn:
        messages = await conn.execute(
            select(Message).where(
                Message.chat == int(chat_id), Message.id >= cursor).order_by(
                Message.time_created.asc()).limit(limit))
    messages = messages.fetchall()
    required_messages = []
    for row in reversed(messages):
        required_messages.append(row[3])
    return required_messages, str(cursor + len(required_messages))


async def post_messages_to_db(chat_id: str,
                              user_id: str,
                              message: str,
                              engine: AsyncEngine):
    async with engine.begin() as conn:
        res = await conn.execute(
            insert(Message, returning=[Message.id]),
            {"user": int(user_id), "chat": int(chat_id), "msg": message})
        return res.fetchall()


async def find_user_in_chat(request: web.Request, chat: str, login: str):
    """
    здесь приходит только логин
    """
    async with request.app['db'].begin() as conn:
        find_login = await conn.execute(
            select(User).where(
                User.chat == int(chat), User.login == login
            )
        )
    if not find_login.fetchall():
        raise NotFoundChatsUsers('user-not-found')


async def create_ans(messages: list, cursor: str):
    new_messages = []
    for message in messages:
        new_messages.append({"text": message})
    new_cursor = {"iterator": cursor}
    return new_messages, new_cursor


class DbMessageManager(BaseMessageManager):
    async def get_messages(self, limit: int,
                           cursor: int,
                           chat_id: str,
                           request: web.Request,
                           engine: AsyncEngine,
                           cache: Optional[ApiCache] = None):
        login = await authentication.get_login(request)
        await find_user_in_chat(request, chat_id, login)    # Исключение если такого юзера нет
        if cache.get_chat(chat_id):
            chat = cache.get_chat(chat_id)
            head_chat = chat.get_head()
            tail_chat = chat.get_tail()
            if head_chat <= cursor <= tail_chat:            # можем получить сообщения из кэша
                messages, cursor = cache.get_messages(
                    chat_id, limit, cursor, is_working_db=True)
                return list(messages), cursor
        messages, cursor = await get_messages_from_db(      # иначе идем в бд
            chat_id, cursor, limit, engine
        )
        messages, cursor = await create_ans(messages, cursor)
        return messages, cursor

    async def post_message(self, chat_id: str,
                           user_id: str,
                           message: str,
                           engine: AsyncEngine,
                           cache: Optional[ApiCache] = None) -> str:
        msg_id = await post_messages_to_db(chat_id, user_id, message, engine)
        cache.update_cache(chat_id, message, msg_id[0][0])
        return str(msg_id[0][0])
