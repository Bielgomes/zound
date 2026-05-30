import traceback
from typing import Coroutine

from utils.errors import (
    EventError,
    MissingFieldError,
    UnsupportedEventError,
)
from utils.events import ErrorEvent
from utils.functions import send_message


class GlobalEventHandler:
    """
    Class to handle global events from the websocket connection.

    This class is responsible for processing incoming events and dispatching them to the appropriate handler.
    """

    __handlers = {}

    @staticmethod
    def register(event: str) -> Coroutine:
        """
        Register a new event handler.

        :param event: The event type to register.
        """

        def wrapper(handler: Coroutine):
            if event in GlobalEventHandler.__handlers:
                raise ValueError(f"❌ Event handler for {event} already registered")

            GlobalEventHandler.__handlers[event] = handler
            print(f"[Global Event Handler] 📦 {event.value} registered event handler")
            return handler

        return wrapper

    @staticmethod
    async def handle_event(event: dict) -> None:
        """
        Handle events received from the websocket connection.

        This function checks the event type and performs the corresponding action.

        :param event: The event received from the client.
        """
        print(f"[Global Event Handler] 📫 Received event: {event}")

        try:
            if not event.get("type"):
                raise MissingFieldError("type")

            handler = GlobalEventHandler.__handlers.get(event["type"])
            if handler is None:
                raise UnsupportedEventError(event["type"])

            await handler(event)

        except EventError as error:
            await send_message(
                {
                    "type": error.type,
                    "error": str(error),
                },
            )
        except Exception as error:
            print(traceback.format_exc())
            await send_message(
                {
                    "type": ErrorEvent.GENERIC_ERROR,
                    "error": str(error),
                },
            )
