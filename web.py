
################ Server receive ping and send pong 
import asyncio
from websockets.asyncio.server import serve

async def echo(websocket):
    async for message in websocket:
        print(message)
        await websocket.send("pong")


async def main():
    async with serve(echo, "10.89.76.206", 8765) as server:
        await server.serve_forever()

if __name__ == "__main__":
    asyncio.run(main())


################### client receive pong and send ping
import asyncio
from websockets.asyncio.client import connect


async def hello():
    async with connect("ws://localhost:8765") as websocket:
        while True:
            await websocket.send("ping")
            # print(f"sent: ping")
            await asyncio.sleep(1)
            message = await websocket.recv()
            print(message)


if __name__ == "__main__":
    asyncio.run(hello())