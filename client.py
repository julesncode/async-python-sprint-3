import asyncio
import base64
import json

import websockets

import config


async def receive_messages():
    async with websockets.connect(f"ws://{config.SERVER_HOST}:{config.SERVER_PORT}/connect") as ws:
        try:
            async for message in ws:
                data = json.loads(message)
                print("Received message:", data)
        except websockets.exceptions.ConnectionClosed as exc:
            print(f"Connection closed unexpectedly: {exc}")


async def send_message(message, recipient=None, comment=None, file_path=None):
    data = {"message": message}
    if recipient:
        data["recipient"] = recipient
    if comment:
        data["comment"] = comment
    if file_path:
        with open(file_path, "rb") as file:
            file_content = file.read()
            file_content_base64 = base64.b64encode(file_content).decode("utf-8")
            data["file_upload"] = True
            data["file_content"] = file_content_base64

    async with websockets.connect(f"ws://{config.SERVER_HOST}:{config.SERVER_PORT}/connect") as ws:
        try:
            await ws.send(json.dumps(data))
        except websockets.exceptions.ConnectionClosed as exc:
            print(f"Connection closed unexpectedly: {exc}")


async def main():
    tasks = []
    if config.CLIENT_RECEIVE_MESSAGES:
        tasks.append(receive_messages())

    send_message_args = (
        config.CLIENT_SEND_MESSAGE,
        config.CLIENT_SEND_RECIPIENT,
        config.CLIENT_SEND_COMMENT,
        config.CLIENT_SEND_FILE_PATH
    )
    tasks.append(send_message(*send_message_args))

    await asyncio.gather(*tasks)


if __name__ == '__main__':
    asyncio.run(main())
