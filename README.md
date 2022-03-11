**REST-API messenger, written on Python. No GUI**

**Stack:** aiohttp, sqlalchemy, alembic, postgresql, redis, pytest

**Features:**
- Registration and authorization
- Chats creating
- Searching messages in chats
- **Individual messages** from "bot" in case if database is unavailable
- Using the **cache** when the database is unavailable
- Errors handling


To start messenger run ```docker-compose up```
