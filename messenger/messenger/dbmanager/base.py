from typing import Optional
from abc import ABC, abstractmethod
from aiohttp import web
from messenger.cache import ApiCache
from sqlalchemy.ext.asyncio import AsyncEngine


class BaseMessageManager(ABC):
    @abstractmethod
    def get_messages(self, limit: int,
                     cursor: int,
                     chat_id: int,
                     request: web.Request,
                     engine: AsyncEngine,
                     cache: Optional[ApiCache] = None):
        raise NotImplementedError

    @abstractmethod
    def post_message(self, chat_id: int,
                     user_id: int,
                     message: str,
                     engine: AsyncEngine,
                     cache: Optional[ApiCache] = None):
        raise NotImplementedError
