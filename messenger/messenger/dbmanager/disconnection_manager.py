from typing import (Optional, Tuple)
from aiohttp import web

from sqlalchemy.ext.asyncio import AsyncEngine

from messenger.dbmanager.base import BaseMessageManager
from messenger.cache.cache import ApiCache
from messenger.dbmanager.connection_manager import create_ans
from messenger.dbmanager.exceptions import (ServiceUnavailable, NotFoundChatsUsers)
from messenger.handlers import authentication


async def find_chat_and_user(chat_id: str, login_req: str) -> Tuple[bool, str]:
    chat_find = False
    user_find = False
    with open('chats-users.txt', 'r+') as fd:
        while True:
            file_line = fd.readline()
            if not file_line:
                break
            file_line = file_line.split()
            chat, login = file_line[0], file_line[1].strip()
            if chat == chat_id and login_req == login:
                return True, 'success'
            if chat == chat_id:
                chat_find = True
            if login == login_req:
                user_find = True
    if not chat_find:
        return False, 'chat-not-found'
    if not user_find or user_find and chat_find:
        return False, 'user-not-found'


# Проверка существования пользователя - чата здесь
class CacheMessageManager(BaseMessageManager):
    async def get_messages(self, limit: int,
                           cursor: int,
                           chat_id: str,
                           request: web.Request,
                           engine: AsyncEngine,
                           cache: Optional[ApiCache] = None):
        login = await authentication.get_login(request)
        login = login.decode('utf-8')
        success, message = await find_chat_and_user(chat_id, login)
        if not success:
            raise NotFoundChatsUsers(message)
        messages, cursor = cache.get_messages(
            chat_id, limit, cursor, is_working_db=False, login=login
        )
        messages, cursor = await create_ans(list(messages), cursor)
        return messages, cursor

    async def post_message(self, chat_id: int,
                           user_id: int,
                           message: str,
                           engine: AsyncEngine,
                           cache: Optional[ApiCache] = None):
        raise ServiceUnavailable()
