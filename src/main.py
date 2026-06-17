import asyncio
import json
import os
import signal

import websockets

from controllers.config_controller import config
from event_handler import EventHandler
from events import *  # noqa: F403
from websocket_state import state


async def echo(websocket: websockets.ServerConnection):
    """
    Handle incoming websocket connections and events.
    This function receives events from the websocket and processes them using the global event handler.

    Uses a global variable to store the connected websocket.

    :param websocket: The websocket connection to handle.
    """

    if state.connected_websocket is None:
        state.connected_websocket = websocket
    if state.connected_websocket.id != websocket.id:
        return

    try:
        while True:
            event = await websocket.recv()
            await EventHandler.handle_event(json.loads(event))
    except websockets.ConnectionClosed:
        print("[Websocket] ❌ Connection closed")
        os.kill(os.getpid(), signal.SIGILL)


async def main():
    state.asyncio_loop = asyncio.get_running_loop()
    async with websockets.serve(echo, config.host, config.port) as server:
        print(f"[Websocket] 🚀 Server started on ws://{config.host}:{config.port}")
        await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(main())
