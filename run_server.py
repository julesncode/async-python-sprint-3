import asyncio
import websockets

import config
from server import Chat


async def main():
    server = Chat()

    async with websockets.serve(
            server.handle_client, host=config.SERVER_HOST, port=config.SERVER_PORT
    ):
        print(f"WebSocket server started on {config.SERVER_HOST}:{config.SERVER_PORT}")

        await asyncio.Future()  # Keep the server running


if __name__ == '__main__':
    asyncio.run(main())
