from database.models import Config
from services.config import ConfigService

config_service = ConfigService()


class ConfigController:
    """
    Singleton class to manage configuration settings for the application.
    This class is designed to be initialized only once and provides access to configuration settings
    """

    def __init__(self) -> None:
        self._host = "localhost"
        self._port = 4358

        self._chunk_size = 1024
        self.__sync_database()

    def __sync_database(self):
        config = config_service.get()

        self._headphone_volume = config.headphone_volume
        self._microphone_volume = config.microphone_volume
        self.headphone_muted = config.headphone_muted

        print(f"[Config] 🔧 Config synced with database: [{config}]")

    def update(self, config: Config):
        self.headphone_volume = config.get("headphone_volume", 0.5)
        self.microphone_volume = config.get("microphone_volume", 0.5)
        self.headphone_muted = config.get("headphone_muted", False)

    @property
    def host(self) -> str:
        return self._host

    @property
    def port(self) -> int:
        return self._port

    @property
    def chunk_size(self) -> int:
        return self._chunk_size

    @property
    def headphone_volume(self) -> float:
        return self._headphone_volume

    @headphone_volume.setter
    def headphone_volume(self, value: float) -> None:
        if 0 <= value <= 1:
            self._headphone_volume = value
        else:
            raise ValueError("Volume must be between 0 and 1.")

    @property
    def microphone_volume(self) -> float:
        return self._microphone_volume

    @microphone_volume.setter
    def microphone_volume(self, value: float) -> None:
        if 0 <= value <= 1:
            self._microphone_volume = value
        else:
            raise ValueError("Volume must be between 0 and 1.")

    @property
    def headphone_muted(self) -> bool:
        return self._headphone_muted

    @headphone_muted.setter
    def headphone_muted(self, value: bool) -> None:
        if isinstance(value, bool):
            self._headphone_muted = value
        else:
            raise ValueError("Muted status must be a boolean.")


config = ConfigController()
