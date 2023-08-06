import asyncio
from typing import Optional

import aiohttp

import config


async def receive_messages() -> None:
    async with aiohttp.ClientSession() as session:
        async with session.ws_connect(f"{config.SERVER_URL}/connect") as ws:
            async for msg in ws:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    data = msg.json()
                    print("Received message:", data)
                elif msg.type == aiohttp.WSMsgType.ERROR:
                    break


async def send_message(message: str, recipient: Optional[str] = None, comment: Optional[str] = None,
                       file_path: Optional[str] = None) -> None:
    data = {"message": message}
    if recipient:
        data["recipient"] = recipient
    if comment:
        data["comment"] = comment
    async with aiohttp.ClientSession() as session:
        if file_path:
            with open(file_path, 'rb') as file:
                data["file"] = aiohttp.FormData()
                data["file"].add_field('file', file.read(), filename=file_path)
            async with session.post(f"{config.SERVER_URL}/upload", data=data["file"]) as response:
                print(await response.text())
        else:
            async with session.ws_connect(f"{config.SERVER_URL}/connect") as ws:
                await ws.send_json(data)


async def main() -> None:
    tasks = []
    if config.CLIENT_RECEIVE_MESSAGES:
        tasks.append(receive_messages())
    tasks.append(send_message(config.CLIENT_SEND_MESSAGE, recipient=config.CLIENT_SEND_RECIPIENT,
                              comment=config.CLIENT_SEND_COMMENT, file_path=config.CLIENT_SEND_FILE_PATH))
    await asyncio.gather(*tasks)


if __name__ == '__main__':
    asyncio.run(main())
