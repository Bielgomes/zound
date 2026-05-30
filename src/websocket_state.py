import websockets


class WebSocketState:
    def __init__(self) -> None:
        self.connected_websocket: websockets.ServerConnection | None = None


state = WebSocketState()
