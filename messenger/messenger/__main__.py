import asyncio

from aiohttp import web

from messenger.server import get_app

loop = asyncio.get_event_loop()
app = loop.run_until_complete(get_app())


def main():
    web.run_app(app, host='0.0.0.0', port=8000)


if __name__=='__main__':
    main()
