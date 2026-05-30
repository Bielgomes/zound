from config_controller import config as config_controller
from database.services.config import ConfigService
from handlers.event_handler import EventHandler
from utils.errors import MissingFieldError
from utils.events import IncomingEvent, OutgoingEvent
from utils.functions import send_message

config_service = ConfigService()


@EventHandler.register(IncomingEvent.CONFIG_FETCH)
async def handle_config_fetch(event: dict) -> None:
    config = config_service.get()
    await send_message(
        {
            "type": OutgoingEvent.CONFIG_FETCHED,
            "config": config.model_dump(),
        },
    )


@EventHandler.register(IncomingEvent.CONFIG_UPDATE)
async def handle_config_update(event: dict) -> None:
    config = event.get("config", None)
    if config is None:
        raise MissingFieldError("config.")

    config_service.update(config)

    config_controller.headphone_volume = config.get("headphone_volume", 0.5)
    config_controller.microphone_volume = config.get("microphone_volume", 0.5)
    config_controller.headphone_muted = config.get("headphone_muted", False)

    await send_message(
        {
            "type": OutgoingEvent.CONFIG_UPDATED,
            "config": config,
        },
    )
