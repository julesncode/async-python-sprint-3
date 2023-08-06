from aiohttp import web

import config
from server import Chat, error_middleware, handle_connect, handle_upload

app = web.Application(middlewares=[error_middleware])

app.router.add_get('/connect', handle_connect)
app.router.add_post('/upload', handle_upload)

web.run_app(app, host=config.SERVER_HOST, port=config.SERVER_PORT)
