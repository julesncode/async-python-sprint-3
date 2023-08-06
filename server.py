import logging
import time
import traceback
from typing import List, Dict

import aiohttp
from aiohttp import web

import config

# Configure logging to save logs to a file
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] [%(module)s:%(lineno)d] %(message)s',
    filename='server.log',
    filemode='a'
)


class Comment:
    def __init__(self, text: str, sender: str):
        self.text = text
        self.sender = sender


class Chat:
    def __init__(self, max_messages: int = 20, message_lifetime: int = 3600,
                 max_message_size: int = 5 * 1024 * 1024, ban_duration: int = 4 * 3600):
        self.messages = []
        self.clients = set()
        self.max_messages = max_messages
        self.message_lifetime = message_lifetime
        self.max_message_size = max_message_size
        self.ban_duration = ban_duration
        self.user_reports = {}  # type: Dict[str, int]

    def add_client(self, client: aiohttp.ClientWebSocketResponse):
        self.clients.add(client)

    def remove_client(self, client: aiohttp.ClientWebSocketResponse):
        self.clients.remove(client)

    def add_message(self, message: str, sender: str):
        timestamp = int(time.time())
        if not self.is_user_banned(sender):
            self.messages.append({"message": message, "sender": sender, "comments": [], "timestamp": timestamp})
            self.cleanup_messages()

    def add_comment(self, message_idx: int, comment_text: str, sender: str):
        if not self.is_user_banned(sender):
            self.messages[message_idx]["comments"].append(Comment(comment_text, sender))

    def get_messages(self, n: int = 20) -> List[Dict]:
        return self.messages[-n:]

    def cleanup_messages(self):
        current_time = int(time.time())
        self.messages = [msg for msg in self.messages if current_time - msg["timestamp"] <= self.message_lifetime]

    def is_user_banned(self, user: str) -> bool:
        ban_time = self.user_reports.get(user, 0)
        if ban_time > time.time():
            return True
        return False

    def report_user(self, user: str):
        if not self.is_user_banned(user):
            self.user_reports[user] = self.user_reports.get(user, 0) + 1
            if self.user_reports[user] >= 3:
                self.ban_user(user)

    def ban_user(self, user: str):
        ban_time = time.time() + self.ban_duration
        self.user_reports[user] = ban_time


async def handle_connect(request: web.Request) -> web.WebSocketResponse:
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    client = ws
    chat.add_client(client)

    try:
        async for msg in ws:
            if msg.type == aiohttp.WSMsgType.TEXT:
                data = msg.json()
                sender = client.remote
                recipient = data.get("recipient")
                message = data.get("message")
                comment = data.get("comment")
                if comment is not None:
                    chat.add_comment(message, comment, sender)
                else:
                    chat.add_message(message, sender)
            elif msg.type == aiohttp.WSMsgType.ERROR:
                break
    finally:
        chat.remove_client(client)

    return ws


async def handle_upload(request: web.Request) -> web.Response:
    reader = await request.multipart()
    file_field = await reader.next()
    if file_field is not None:
        filename = file_field.filename
        content = await file_field.read()

    return web.Response(text="File uploaded successfully.")


async def error_middleware(app: web.Application, handler) -> web.Response:
    async def middleware_handler(request):
        try:
            return await handler(request)
        except web.HTTPException as ex:
            return web.Response(text=str(ex), status=ex.status)
        except Exception as ex:
            logging.error(traceback.format_exc())
            return web.Response(text="Internal Server Error", status=500)

    return middleware_handler


chat = Chat(max_messages=config.MAX_MESSAGES, message_lifetime=config.MESSAGE_LIFETIME,
            max_message_size=config.MAX_MESSAGE_SIZE)
