import asyncio
import random
import string

from aiohttp import web
from pydantic import ValidationError
from sqlalchemy import select, func
from sqlalchemy.exc import InterfaceError
from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine
from sqlalchemy.orm import sessionmaker

from messenger.db import Message, User
from messenger.db.models import TaskMessages
from messenger.dbmanager.connection_manager import create_ans
from messenger.handlers.authentication import get_login
from messenger.handlers.responses import bad_parameters_error, task_created, task_not_found, send_status_task, response_messages
from messenger.utils import logger, validators
from messenger.utils.message_params import get_limit, get_cursor


async def get_messages_from_task_db(request: web.Request, task_id: str, limit: int, cursor: int):
    engine = request.app['db']
    async_session = sessionmaker(
        engine, expire_on_commit=False, class_=AsyncSession)
    async with async_session() as session:
        async with session.begin():
            res = await session.execute(
                select(TaskMessages).
                    where(TaskMessages.task_id == task_id).
                    order_by(TaskMessages.time_created.asc()).
                    limit(limit))
        messages = [msg.msg for msg in res.scalars()]
        messages = messages[(cursor - 1):limit]
        messages.reverse()
        cursor = min(cursor + limit, len(messages) + 1)
        messages, cursor = await create_ans(list(messages), str(cursor))
        return messages, cursor


@logger.logger
async def get_messages_from_task(request: web.Request):
    task_id = request.match_info.get('task_id')
    limit = await get_limit(request)
    cursor = await get_cursor(request)
    if not task_id or not limit:
        return await bad_parameters_error()
    tasks = request.app['tasks']
    task = tasks.get(task_id)
    if not task or task[0] == 'FAILED':
        return await task_not_found()
    await task[1]
    if task[0] == 'FAILED':
        return await task_not_found()
    messages, cursor = await get_messages_from_task_db(request, task_id, limit, cursor)
    task[0] = 'SUCCESS'
    return await response_messages(messages, cursor, True)


@logger.logger
async def get_status_task(request: web.Request):
    task_id = request.match_info.get('task_id')
    if not task_id:
        return await bad_parameters_error()
    tasks = request.app['tasks']
    task = tasks.get(task_id)
    if not task:
        return await task_not_found()
    status = task[0]
    return await send_status_task(status)


async def searching(engine: AsyncEngine,
                    tasks: dict,
                    task_id: str,
                    message: str,
                    login: str):
    async_session = sessionmaker(
        engine, expire_on_commit=False, class_=AsyncSession)
    try:
        async with async_session() as session:
            async with session.begin():
                res = await session.execute(
                    select(Message).
                        join(User).
                        where(User.login == login).
                        where(func.to_tsvector(Message.msg).
                              match(message, postgresql_regconfig="english"
                                    )))
                '''
                здесь можно раскомментировать, чтобы увидеть выполнение таски
                '''
                # for i in range(30):
                #     await asyncio.sleep(1)
                objects = [TaskMessages(task_id=task_id, msg=msg.msg) for msg in res.scalars()]
                objects = objects[:100]
                session.add_all(objects)
        tasks[task_id][0] = 'WAITING'
    except (ConnectionRefusedError, InterfaceError):
        tasks[task_id][0] = 'FAILED'


@logger.logger
async def search_messages(request: web.Request):
    login = await get_login(request)
    try:
        data = await request.text()
        message = validators.SearchMessage.parse_raw(data)
        task_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
        """
        tasks: key = task_id, [0] - status, [1] - coroutine
        """
        engine = request.app['db']
        tasks = request.app['tasks']
        task = asyncio.create_task(searching(engine, tasks, task_id, message.message, login))
        tasks[task_id] = ['IN PROCESS', task]
        return await task_created(task_id)
    except ValidationError:
        return await bad_parameters_error()
