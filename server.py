import json
import time
from typing import List, Dict
from collections import OrderedDict

import websockets

import config
from logger import setup_logger, get_logger

setup_logger('server.log')
logger = get_logger('server')


class Comment:
    def __init__(self, text: str, sender: str):
        self.text = text
        self.sender = sender


class Chat:
    def __init__(self, max_messages: int = 20, message_lifetime: int = 3600,
                 max_message_size: int = 5 * 1024 * 1024, ban_duration: int = 4 * 3600):
        self.messages = OrderedDict()
        self.clients = set()
        self.max_messages = max_messages
        self.message_lifetime = message_lifetime
        self.max_message_size = max_message_size
        self.ban_duration = ban_duration
        self.user_reports: Dict[str, int] = {}

    def add_client(self, client):
        self.clients.add(client)

    def remove_client(self, client):
        self.clients.remove(client)

    def add_message(self, message: str, sender: str):
        timestamp = int(time.time())
        message_data = {"sender": sender, "comments": [], "timestamp": timestamp}
        if not self.is_user_banned(sender):
            self.messages[message] = message_data
            self.cleanup_messages()

    def get_messages(self, n: int = 20) -> OrderedDict:
        messages = OrderedDict()
        for key in list(self.messages.keys())[-n:]:
            messages[key] = self.messages[key]
        return messages

    def cleanup_messages(self):
        current_time = int(time.time())
        self.messages = OrderedDict((key, value) for key, value in self.messages.items() if
                                    current_time - value["timestamp"] <= self.message_lifetime)

        if len(self.messages) > self.max_messages:
            messages = OrderedDict()
            for key in list(self.messages.keys())[-self.max_messages:]:
                messages[key] = self.messages[key]
            self.messages = messages


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

    def add_comment(self, message: str, comment_text: str, sender: str):
        if message in self.messages:
            if not self.is_user_banned(sender):
                self.messages[message]["comments"].append(Comment(comment_text, sender))

        else:
            # Handle an invalid message index here, such as logging a warning or ignoring the comment
            print("Invalid message index:", message)

    async def handle_upload(self, ws, data):
        file = data.get("file_upload", False)
        if file:
            content = data.get("file_content", None)
            if content:
                content = content.encode()  # Assuming the file content is sent as a base64-encoded string

                # Notify the client that the file upload was successful
                response = {"status": "success", "message": "File uploaded successfully."}
                await ws.send(json.dumps(response))
            else:
                response = {"status": "error", "message": "Problems with file contents."}
                await ws.send(json.dumps(response))
        else:
            # No file in the request
            response = {"status": "error", "message": "No file uploaded."}
            await ws.send(json.dumps(response))

    async def handle_client(self, ws):
        self.clients.add(ws)
        try:
            async for message in ws:
                data = json.loads(message)
                sender = ws.remote_address[0]
                msg_content = data.get("message")
                comment = data.get("comment")
                file_upload = data.get("file_upload")

                if file_upload:
                    await self.handle_upload(ws, data)
                elif comment is not None:
                    self.add_comment(msg_content, comment, sender)
                else:
                    self.add_message(msg_content, sender)
        except websockets.ConnectionClosed:
            pass
        finally:
            self.clients.remove(ws)
