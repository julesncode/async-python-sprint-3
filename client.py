import json
import trio
import trio_websocket
from trio_websocket import open_websocket_url

import config

async def receive_messages():
    async with open_websocket_url(f"ws://{config.SERVER_HOST}:{config.SERVER_PORT}/connect") as ws:
        async for msg in ws:
            if msg.type == trio_websocket.MessageType.text:
                data = json.loads(msg.data)
                print("Received message:", data)
            elif msg.type == trio_websocket.MessageType.close:
                break

async def send_message(message, recipient=None, comment=None, file_path=None):
    data = {"message": message}
    if recipient:
        data["recipient"] = recipient
    if comment:
        data["comment"] = comment

    async with open_websocket_url(f"ws://{config.SERVER_HOST}:{config.SERVER_PORT}/connect") as ws:
        await ws.send_text(json.dumps(data))

async def main():
    async with trio.open_nursery() as nursery:
        if config.CLIENT_RECEIVE_MESSAGES:
            nursery.start_soon(receive_messages)

        send_message_args = (
            config.CLIENT_SEND_MESSAGE,
            config.CLIENT_SEND_RECIPIENT,
            config.CLIENT_SEND_COMMENT,
            config.CLIENT_SEND_FILE_PATH
        )
        nursery.start_soon(send_message, *send_message_args)

if __name__ == '__main__':
    trio.run(main)
