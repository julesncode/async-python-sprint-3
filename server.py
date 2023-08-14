import logging
import json
import time
import websockets

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

    def add_comment(self, message: str, comment_text: str, sender: str):
        if message in self.messages:
            self.messages[message]["comments"].append(Comment(comment_text, sender))
        else:
            # Handle an invalid message index here, such as logging a warning or ignoring the comment
            print("Invalid message index:", message)

    def cleanup_messages(self):
        current_time = int(time.time())
        self.messages = [msg for msg in self.messages if current_time - msg["timestamp"] <= config.MESSAGE_LIFETIME]

    async def handle_upload(self, ws, data):
        if "file" in data:
            filename = data.get("filename", "unknown.txt")
            content = data["file"].encode()  # Assuming the file content is sent as a base64-encoded string

            # Process the uploaded file content or save it
            # You can add your code here to handle the uploaded file

            # Notify the client that the file upload was successful
            response = {"status": "success", "message": "File uploaded successfully."}
            await ws.send(json.dumps(response))
        else:
            # No file in the request
            response = {"status": "error", "message": "No file uploaded."}
            await ws.send(json.dumps(response))

    async def handle_client(self, ws, path):
        self.clients.add(ws)
        try:
            async for message in ws:
                data = json.loads(message)
                sender = ws.remote_address[0]
                recipient = data.get("recipient")
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
