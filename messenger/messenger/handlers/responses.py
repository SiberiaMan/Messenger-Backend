from aiohttp import web
from messenger.utils import logger
from sqlalchemy.exc import IntegrityError


async def send_status_task(task_status: str):
    data = {"status": task_status}
    await logger.write_log('[TASK STATUS SUCCESS]\n')
    return web.json_response(data, status=200)


async def task_not_found():
    data = {"message": "task-not-found"}
    await logger.write_log('[TASK NOT FOUND]\n')
    return web.json_response(data, status=404)


async def task_created(task_id: str):
    data = {"task_id": task_id}
    await logger.write_log('[SUCCESS CREATED]\n')
    return web.json_response(data, status=201)


async def registration_success():
    data = {"message": "registration completed successfully"}
    await logger.write_log('[SUCCESS REGISTRATION CREATED]\n')
    return web.json_response(data, status=201)


async def registration_fail():
    data = {"message": "login already in use"}
    await logger.write_log('[FAIL REGISTRATION FAILED]\n')
    return web.json_response(data, status=400)


async def not_login_or_password(text: str):
    data = {"message": text}
    await logger.write_log('[LOGIN OR PASSWORD REQUIRED]\n')
    return web.json_response(data, status=401)


async def wrong_login_or_password():
    data = {"message": "wrong login or password"}
    await logger.write_log('[WRONG LOGIN OR PASSWORD]\n')
    return web.json_response(data, status=401)


async def repeat_chat():
    data = {"message": "chat is already exists"}
    await logger.write_log('[CHAT REPEATING]\n')
    return web.json_response(data, status=400)  # TODO correct http-statuses


async def repeat_user():
    data = {"message": "user already exists in this chat"}
    await logger.write_log('[USER ALREADY EXISTS]\n')
    return web.json_response(data, status=400) # TODO correct http-statuses


async def db_available():
    await logger.write_log('[DB AVAILABLE]\n')
    return web.Response(status=200)


async def db_unavailable():
    data = {"message": "database is not available yet"}
    await logger.write_log('[DB UNAVAILABLE]\n')
    return web.json_response(data, status=503)


async def bad_parameters_error():
    data = {"message": "bad-parameters"}
    await logger.write_log('[FAILURE BAD-PARAMETERS]\n')
    return web.json_response(data, status=400)


async def not_found(ex: IntegrityError):
    message = 'chat-not-found' if 'chats' in ex.args[0] else 'user-not-found'
    data = {"message": message}
    await logger.write_log(f'[{message.upper()}]' + '\n')
    return web.json_response(data, status=404)


async def get_not_found(text: str):
    data = {"message": text}
    await logger.write_log(f'[{text.upper()}]' + '\n')
    return web.json_response(data, status=404)


async def create_response(id: str, message: str):
    data = {id: message}
    await logger.write_log('[SUCCESS CREATED]\n')
    return web.json_response(data, status=201)


async def response_messages(messages: list, cursor: str, conn: bool):
    data = {
        "messages": messages,
        "next": cursor
    }
    await logger.write_log('[SUCCESS ACCEPTED]\n')
    if conn:
        return web.json_response(data, status=200)
    else:
        await logger.write_log('[DB UNAVAILABLE]\n')
        return web.json_response(data, status=503)


async def service_unavailable():
    data = {
        "message": "service_unavailable"
    }
    await logger.write_log('[DB UNAVAILABLE]\n')
    return web.json_response(data, status=503)


async def server_error():
    data = {
        "message": "Something happened on the server, but the founding father foresaw it"
    }
    await logger.write_log('[UNEXPECTED ERROR ON SERVER]\n')
    return web.json_response(data, status=500)
