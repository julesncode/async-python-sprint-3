import logging
import json
import time
import functools
import trio
from trio_websocket import serve_websocket

import config

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
    def __init__(self):
        self.messages = []
        self.clients = set()

    def add_client(self, client):
        self.clients.add(client)

    def remove_client(self, client):
        self.clients.remove(client)

    def add_message(self, message: str, sender: str):
        timestamp = int(time.time())
        self.messages.append({"message": message, "sender": sender, "comments": [], "timestamp": timestamp})
        self.cleanup_messages()

    def add_comment(self, message_idx: int, comment_text: str, sender: str):
        self.messages[message_idx]["comments"].append(Comment(comment_text, sender))

    def cleanup_messages(self):
        current_time = int(time.time())
        self.messages = [msg for msg in self.messages if current_time - msg["timestamp"] <= config.MESSAGE_LIFETIME]


chat = Chat()


async def handle_client(ws, _):
    chat.add_client(ws)
    try:
        async for message in ws:
            data = json.loads(message)
            sender = ws.remote_address[0]
            recipient = data.get("recipient")
            msg_content = data.get("message")
            comment = data.get("comment")
            if comment is not None:
                chat.add_comment(msg_content, comment, sender)
            else:
                chat.add_message(msg_content, sender)
    except trio_websocket.ConnectionClosed:
        pass
    finally:
        chat.remove_client(ws)


async def main():
    await serve_websocket(
        handler=handle_client,
        ssl_context=None,  # Provide your SSL context here if needed
        host=config.SERVER_HOST,
        port=config.SERVER_PORT,
    )


if __name__ == '__main__':
    trio.run(main)
