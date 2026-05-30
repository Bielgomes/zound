import json

from database.models import Sound
from database.services.sound import SoundService
from utils.events import OutgoingEvent
from websocket_state import state


async def send_message(message: json) -> None:
    """
    Send a message to the client.

    :param message: The message to send.
    """
    if state.connected_websocket is None:
        raise RuntimeError("No connected websocket.")

    if not isinstance(message, dict):
        raise ValueError("Message must be a dictionary.")

    await state.connected_websocket.send(json.dumps(message))


async def update_sound_is_valid_and_notify(
    sound_service: SoundService, sound: Sound, is_valid: bool
) -> None:
    sound.is_valid = is_valid
    sound_service.set_is_valid(sound.id, is_valid=is_valid)
    message = {"type": OutgoingEvent.SOUND_UPDATED, "sound": sound.model_dump()}
    await send_message(message)
