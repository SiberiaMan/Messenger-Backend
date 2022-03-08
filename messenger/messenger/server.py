import os
import asyncpg
import redis
from aiohttp import web
from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import create_async_engine

from messenger.db import Login
from messenger.handlers.search_handlers import search_messages, get_status_task, get_messages_from_task
from messenger.utils import logger
from messenger.handlers import chat_handlers, message_handlers, middleware
from messenger.cache import ApiCache
from messenger.handlers.middleware import registration, authorization

switcher = 1


async def handle_connection(request: web.Request):
    global switcher
    if switcher % 2:
        engine = create_async_engine(
            'postgresql+asyncpg://user:pswd@localhost:5431/my_db',
        )
    else:
        engine = create_async_engine(
            'postgresql+asyncpg://user:pswd@localhost:5432/my_db',
        )
    switcher += 1
    request.app['db'] = engine


routes = [
    web.post('/v1/registration', registration),
    web.post('/v1/authorization', authorization),
    web.post('/v1/chats/search', search_messages),
    web.get('/v1/chats/search/status/{task_id}', get_status_task),
    web.get('/v1/chats/search/{task_id}/messages', get_messages_from_task),
    web.get('/v1/handle_connection', handle_connection),
    web.get('/v1/ping_db', chat_handlers.ping_db),
    web.get('/v1/chats/{chat_id}/messages', message_handlers.get_messages),
    web.post('/v1/chats', chat_handlers.chat_create),
    web.post('/v1/chats/{chat_id}/users', chat_handlers.user_create),
    web.post('/v1/chats/{chat_id}/messages', message_handlers.send_message)
]


def get_url():
    return "postgresql+asyncpg://%s:%s@%s/%s" % (
        os.getenv("POSTGRES_USER"),
        os.getenv("POSTGRES_PWD"),
        os.getenv("POSTGRES_HOSTS"),
        os.getenv("POSTGRES_DB"),
    )


print(get_url())


async def app_builtins(app: web.Application):
    app.add_routes(routes)
    engine = create_async_engine(get_url())
    app['db'] = engine
    app['cache'] = ApiCache()
    app['tasks'] = {}
    app['session_login'] = redis.Redis(host='redis', port=6379)
    async with engine.begin() as conn:
        await conn.execute(insert(Login),
                           {"login": "login",
                            "password": "password"
                            })


@logger.logger
async def get_app() -> web.Application:
    app = web.Application(middlewares=[middleware.middleware])
    await app_builtins(app)
    try:
        async with app['db'].begin() as conn:
            await conn.execute(select(1))
    except ConnectionRefusedError as e:
        await logger.write_log('[Cannot connect to db]\n'.upper())
    else:
        await logger.write_log('[Connecting to db]\n'.upper())
    return app
