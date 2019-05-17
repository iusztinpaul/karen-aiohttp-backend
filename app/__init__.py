# -*- coding: utf-8 -*-
from aiohttp import web
from .routes import setup as setup_routers
from .middlewares import setup as setup_middlewares


async def on_startup(app):
    pass


async def on_shutdown(app):
    pass


def create(conf=None):
    if conf is None:
        from .config import Main
        conf = Main

    middlewares = setup_middlewares(conf)

    app = web.Application(middlewares=middlewares)
    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)

    conf.setup(app)
    setup_routers(app)

    return app
