import asyncio
import threading

import sounddevice as sd
import soundfile as sf

from controllers.config_controller import config
from utils.errors import (
    PlaybackDeviceAmbiguousError,
    PlaybackDeviceNotFoundError,
)
from utils.events import OutgoingEvent
from utils.functions import send_message


class SoundController:
    """
    Singleton class to manage sound playback using SoundDevice and SoundFile.
    This class is responsible for playing sound files and managing the playback thread.
    """

    def __init__(self) -> None:
        self._stop_event: threading.Event | None = threading.Event()
        self._playback_thread: threading.Thread | None = None

        self._sound_file: sf.SoundFile | None = None
        self._streamed: int = 0

    def stop_sound(self):
        """
        Stop the currently playing sound and close the playback thread.
        """

        self._streamed = 0
        self._stop_event.set()

        if self._playback_thread and self._playback_thread.is_alive():
            self._playback_thread.join()

        if self._sound_file is not None:
            self._sound_file.close()
            self._sound_file = None

    async def play_sound(
        self,
        sound_path: str,
        sound_id: int,
        loop: asyncio.AbstractEventLoop,
    ):
        """
        Play a sound file using SoundDevice and SoundFile.
        This method will stop any currently playing sound before starting a new one.

        :param sound_path: Path to the sound file to be played.
        :param sound_id: ID of the sound being played.
        :param loop: The asyncio event loop to run the coroutine in.
        """

        self.stop_sound()
        self._stop_event.clear()

        playback_device = await self.__get_playback_device()
        self._playback_thread = threading.Thread(
            target=self.__play_sound,
            args=(playback_device, sound_path, sound_id, loop),
        )
        self._playback_thread.start()

    def __play_sound(
        self,
        device_id: int,
        sound_path: str,
        sound_id: int,
        loop: asyncio.AbstractEventLoop,
    ):
        self._sound_file = sf.SoundFile(sound_path)

        input_stream = sd.OutputStream(
            blocksize=config.chunk_size,
            samplerate=self._sound_file.samplerate,
            channels=self._sound_file.channels,
            dtype="float32",
        )
        output_stream = sd.OutputStream(
            device=device_id,
            blocksize=config.chunk_size,
            samplerate=self._sound_file.samplerate,
            channels=self._sound_file.channels,
            dtype="float32",
        )

        input_stream.start()
        output_stream.start()

        asyncio.run_coroutine_threadsafe(
            send_message(
                {
                    "type": OutgoingEvent.SOUND_PLAYING,
                    "soundId": sound_id,
                },
            ),
            loop,
        )

        self._streamed = 0
        while self._streamed + config.chunk_size < len(self._sound_file):
            if self._stop_event.is_set():
                break

            chunk = self._sound_file.read(config.chunk_size, dtype="float32")

            input_stream.write(
                chunk * (config.headphone_volume if not config.headphone_muted else 0)
            )
            output_stream.write(chunk * config.microphone_volume)

            self._streamed += config.chunk_size

        self._sound_file = None
        self._streamed = 0

        input_stream.close()
        output_stream.close()

        asyncio.run_coroutine_threadsafe(
            send_message(
                {
                    "type": OutgoingEvent.SOUND_STOPPED,
                    "soundId": sound_id,
                },
            ),
            loop,
        )

    async def __get_playback_device(self) -> int:
        """
        Get the device ID of the Input device.
        """

        devices = sd.query_devices()

        voicemeeter_playback = [
            device["index"]
            for device in devices
            if "voicemeeter input (vb-audio voi" in device["name"].lower()
            and device["hostapi"] == 0
        ]

        if not voicemeeter_playback:
            raise PlaybackDeviceNotFoundError("Voicemeeter Input device not found.")

        if len(voicemeeter_playback) > 1:
            raise PlaybackDeviceAmbiguousError(
                "Multiple Voicemeeter Input devices found."
            )

        return voicemeeter_playback[0]


sound_controller = SoundController()
