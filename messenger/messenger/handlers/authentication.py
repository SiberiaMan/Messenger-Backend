from typing import Optional
from aiohttp import web


async def get_login(request: web.Request) -> Optional[str]:
    session_id = request.headers.get('session_id')
    login = request.app['session_login'].get(session_id)
    login = login.decode('utf-8')
    return login
