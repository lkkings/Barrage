import asyncio

import websockets

from barrage import BarrageBuilder

live_uri = ""
ws_uri = ""


async def connect_to_websocket_server():
    async with websockets.connect(ws_uri) as websocket:
        async def callback(message: str):
            websocket.send(message)

        barrage = BarrageBuilder().douyin() \
            .page(live_uri) \
            .port(8080) \
            .on(callback) \
            .build()
        barrage.daemon = True
        barrage.start()
        while True:
            reply = await websocket.recv()
            barrage.send(reply)


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(connect_to_websocket_server())
