from aiohttp import web
from app import create

app = create()
web.run_app(app)
