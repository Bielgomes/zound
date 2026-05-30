import json

from websocket_state import state


async def send_message(message: json) -> None:
    """
    Send a message to the client.

    :param message: The message to send.
    """
    if state.connected_websocket is None:
        raise RuntimeError("No connected websocket")

    if not isinstance(message, dict):
        raise ValueError("Message must be a dictionary")

    await state.connected_websocket.send(json.dumps(message))
