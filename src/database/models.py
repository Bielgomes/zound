import re
from typing import Optional

from pydantic import BaseModel, Field, field_validator

hotkey_regex = re.compile(r"^(?:<[a-zA-Z0-9]+>|[^+])(?:\+(?:<[a-zA-Z0-9]+>|[^+]))*$")


class Sound(BaseModel):
    id: Optional[str] = Field(default=None, title="Sound ID")
    name: str = Field(..., min_length=1, max_length=255, title="Sound Name")
    path: str = Field(..., min_length=1, max_length=255, title="Sound Path")
    hotkey: Optional[str] = Field(default=None, title="Hotkey")
    is_valid: bool = Field(default=True, title="Is Valid")
    created_at: Optional[str] = Field(None, title="Creation Date")

    @field_validator("path")
    @classmethod
    def validate_path(cls, path: any) -> str:
        """
        Validate the sound path to ensure it ends with .mp3 or .wav.
        """

        if not isinstance(path, str):
            raise ValueError("Sound path must be a string.")

        if not path.endswith((".mp3", ".wav")):
            raise ValueError("Sound path must end with .mp3 or .wav.")

        return path

    @field_validator("hotkey")
    @classmethod
    def validate_hotkey(cls, hotkey: any) -> str:
        if hotkey is None:
            return None

        if not isinstance(hotkey, str):
            raise ValueError("Sound hotkey must be a string.")

        if not hotkey_regex.fullmatch(hotkey):
            raise ValueError(
                "Invalid hotkey format. (e.g., 'a', '<alt>+h', '<ctrl>+<shift>+c')"
            )

        return hotkey


class UpdateSound(BaseModel):
    id: str = Field(title="Sound ID")
    name: Optional[str] = Field(
        default=None, min_length=1, max_length=255, title="Sound Name"
    )
    path: Optional[str] = Field(
        default=None, min_length=1, max_length=255, title="Sound Path"
    )

    @field_validator("path")
    @classmethod
    def validate_path(cls, path: any) -> str:
        """
        Validate the sound path to ensure it ends with .mp3 or .wav.
        """

        if not isinstance(path, str):
            raise ValueError("Sound path must be a string.")

        if not path.endswith((".mp3", ".wav")):
            raise ValueError("Sound path must end with .mp3 or .wav.")

        return path


class Config(BaseModel):
    headphone_volume: float = Field(
        default=0.5, ge=0.0, le=1.0, title="Headphone Volume"
    )
    microphone_volume: float = Field(
        default=0.5, ge=0.0, le=1.0, title="Microphone Volume"
    )
    headphone_muted: bool = Field(default=False, title="Headphone Muted")
