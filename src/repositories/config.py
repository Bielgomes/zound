from database.models import Config
from repositories.abstract_repository import AbstractRepository


class ConfigRepository(AbstractRepository):
    """
    Repository for managing config record in the database.
    """

    def __init__(self):
        super().__init__()

    def get(self) -> Config | None:
        self._cursor.execute(
            """
            SELECT headphone_volume, microphone_volume, headphone_muted
            FROM config
            LIMIT 1
            """
        )

        row = self._cursor.fetchone()
        if row:
            return Config(
                headphone_volume=row[0],
                microphone_volume=row[1],
                headphone_muted=row[2],
            )

        return None

    def update(self, config: Config) -> None:
        self._cursor.execute(
            """
            UPDATE config
            SET headphone_volume = ?, microphone_volume = ?, headphone_muted = ?
            WHERE id = 1
            """,
            (config.headphone_volume, config.microphone_volume, config.headphone_muted),
        )
        self._commit()
