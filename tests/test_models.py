import pytest

from streamstats.errors import InvalidEventError
from streamstats.models import parse_event, parse_timestamp

BASE = {"level": "INFO", "source": "db", "message": "m"}


def test_naive_timestamp_gets_utc():
    assert parse_timestamp("2024-05-01T12:00:00").tzinfo is not None


def test_timestamp_not_a_string():
    with pytest.raises(InvalidEventError):
        parse_event({**BASE, "timestamp": 123})


def test_unknown_level():
    with pytest.raises(InvalidEventError):
        parse_event({**BASE, "timestamp": "2024-05-01T12:00:00Z", "level": "FATAL"})


def test_empty_source():
    with pytest.raises(InvalidEventError):
        parse_event({**BASE, "timestamp": "2024-05-01T12:00:00Z", "source": "  "})
