import asyncio
from typing import Dict

from pynput import keyboard

from event_handler import EventHandler
from services.sound import SoundService
from utils.events import IncomingEvent
from websocket_state import state

sound_service = SoundService()


class KeyboardController:
    def __init__(self):
        self._hotkeys: Dict[str, int] = {}
        self.__listener = None

        print("[Keyboard Controller] ✨ Initializing Keyboard listener...")
        self.__initialize_hotkeys()
        self.__create_listener()
        print("[Keyboard Controller] ✅ Keyboard listener initialized successfully!")

    def update_hotkey(self, sound_id: str, hotkey: str):
        hotkeys_values = list(self._hotkeys.values())
        if sound_id in hotkeys_values:
            old_hotkey = list(self._hotkeys.keys())[hotkeys_values.index(sound_id)]
            del self._hotkeys[old_hotkey]

        self._hotkeys[hotkey] = sound_id

        print("[Keyboard Controller] ✨ Recreating listener...")
        self.__create_listener()
        print("[Keyboard Controller] ✅ Keyboard listener recreated successfully!")

    def __initialize_hotkeys(self):
        sounds = sound_service.get_all()
        self._hotkeys = {
            sound["hotkey"]: sound["id"]
            for sound in sounds
            if sound["hotkey"] is not None
        }
        print(f"[Keyboard Controller] 🔧 Hoykeys synced with database: {self._hotkeys}")

    def __create_listener(self):
        if self.__listener:
            self.__listener.stop()
            self.__listener = None

        hotkeys_map = {
            key: lambda v=value: self.on_press_hotkey(sound_id=v)
            for key, value in self._hotkeys.items()
        }

        self.__listener = keyboard.GlobalHotKeys(hotkeys_map)
        self.__listener.start()

    def on_press_hotkey(self, sound_id: str):
        asyncio.run_coroutine_threadsafe(
            EventHandler.handle_event(
                {"type": IncomingEvent.SOUND_PLAY.value, "soundId": sound_id}
            ),
            state.asyncio_loop,
        )


keyboard_controller = KeyboardController()
