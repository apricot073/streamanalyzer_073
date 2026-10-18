from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum

from .errors import InvalidEventError, InvalidTimestampError


class Level(StrEnum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

    def is_error(self) -> bool:
        return self in (Level.ERROR, Level.CRITICAL)

class Event:
    __slots__ = ("level", "message", "source", "timestamp")

    def __init__(self, timestamp: datetime, level: Level, source: str, message: str):
        self.timestamp = timestamp
        self.level = level
        self.source = source
        self.message = message

    def __repr__(self) -> str:
        return (f"Event(timestamp={self.timestamp!r}, level={self.level!r}, "
                f"source={self.source!r}, message={self.message!r})")


def parse_timestamp(value):
    """Разобрать ISO 8601 и вернуть datetime (UTC, если пояса нет)."""
    if not isinstance(value, str) or not value.strip():
        raise InvalidTimestampError(f"неверная временная метка: {value!r}")
    try:
        ts = datetime.fromisoformat(value.strip())
    except ValueError as exc:
        raise InvalidTimestampError(f"неверная временная метка: {value!r}") from exc
    if ts.tzinfo is None:
        ts = ts.replace(tzinfo=UTC)
    return ts


def parse_event(data: dict) -> Event:
    """Создать событие из словаря (csv, jsonl)."""
    missing = [f for f in ("timestamp", "level", "source", "message") if data.get(f) is None]
    if missing:
        raise InvalidEventError(
            f"отсутствуют обязательные поля: {', '.join(missing)}"
        )

    raw_level, source, message = data["level"], data["source"], data["message"]

    if not isinstance(raw_level, str):
        raise InvalidEventError(f"неверный level: {raw_level!r}")
    try:
        level = Level(raw_level.strip().upper())
    except ValueError:
        raise InvalidEventError(f"неизвестный level: {raw_level!r}") from None

    if not isinstance(source, str) or not source.strip():
        raise InvalidEventError("source должен быть непустой строкой")
    if not isinstance(message, str):
        raise InvalidEventError("message должен быть строкой")

    return Event(
        timestamp=parse_timestamp(data["timestamp"]),
        level=level,
        source=source.strip(),
        message=message,
    )