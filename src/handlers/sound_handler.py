import asyncio
from pathlib import Path

from database.services.sound import SoundService
from handlers.global_event_handler import GlobalEventHandler
from sound_controller import sound_controller
from utils.errors import (
    MissingFieldError,
)
from utils.events import IncomingEvent, OutgoingEvent
from utils.functions import send_message, update_sound_is_valid_and_notify

sound_service = SoundService()


@GlobalEventHandler.register(IncomingEvent.SOUND_ADD)
async def handle_sound_add(event: dict) -> None:
    sound = event.get("data", None)
    if sound is None:
        raise MissingFieldError("data")

    new_sound = sound_service.create(sound)
    await send_message(
        {"type": OutgoingEvent.SOUND_ADDED, "sound": new_sound},
    )


@GlobalEventHandler.register(IncomingEvent.SOUND_UPDATE)
async def handle_sound_update(event: dict) -> None:
    sound = event.get("data", None)
    if sound is None:
        raise MissingFieldError("data")

    updated_sound = sound_service.update(sound["id"], sound)
    await send_message(
        {"type": OutgoingEvent.SOUND_UPDATED, "sound": updated_sound},
    )


@GlobalEventHandler.register(IncomingEvent.SOUND_REMOVE)
async def handle_sound_remove(event: dict) -> None:
    sound_id = event.get("soundId", None)
    if sound_id is None:
        raise MissingFieldError("soundId")

    sound_service.delete(sound_id)
    await send_message(
        {"type": OutgoingEvent.SOUND_REMOVED, "soundId": sound_id},
    )


@GlobalEventHandler.register(IncomingEvent.SOUND_FETCH)
async def handle_sound_fetch(event: dict) -> None:
    sounds = sound_service.get_all()
    await send_message(
        {"type": OutgoingEvent.SOUND_FETCHED, "sounds": sounds},
    )


@GlobalEventHandler.register(IncomingEvent.SOUND_PLAY)
async def handle_sound_play(event: dict) -> None:
    sound_id = event.get("soundId", None)
    if sound_id is None:
        raise MissingFieldError("soundId")

    sound = sound_service.get(sound_id)
    is_sound_path_valid = Path(sound.path).is_file()

    if is_sound_path_valid is True and not sound.is_valid:
        await update_sound_is_valid_and_notify(
            sound_service=sound_service, sound=sound, is_valid=True
        )
    elif is_sound_path_valid is False and sound.is_valid:
        return await update_sound_is_valid_and_notify(
            sound_service=sound_service, sound=sound, is_valid=False
        )

    if not is_sound_path_valid:
        return

    await sound_controller.play_sound(sound.path, sound_id, asyncio.get_event_loop())


@GlobalEventHandler.register(IncomingEvent.SOUND_STOP)
async def handle_sound_stop(_) -> None:
    sound_controller.stop_sound()
