import asyncio

import websockets


class WebSocketState:
    def __init__(self) -> None:
        self.connected_websocket: websockets.ServerConnection | None = None
        self.asyncio_loop: asyncio.AbstractEventLoop | None = None


state = WebSocketState()
