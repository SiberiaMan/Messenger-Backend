from aiohttp import web
from typing import Optional


async def get_cursor(request: web.Request) -> int:
    cursor = request.rel_url.query.get('from')
    if not cursor:
        return 1
    try:
        cursor = int(cursor) # плохой курсор
        if cursor <= 0:
            raise ValueError
    except ValueError:
        return 1
    return cursor


async def get_limit(request: web.Request) -> Optional[int]:
    limit = request.rel_url.query.get('limit')
    if not limit:
        return None
    try:
        limit = int(limit)
    except ValueError:
        return None
    return limit
