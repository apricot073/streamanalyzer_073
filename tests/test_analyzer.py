from streamstats.analysis import Stats
from streamstats.models import parse_event


def ev(level, source, ts="2024-05-01T12:00:00Z"):
    return parse_event({"timestamp": ts, "level": level, "source": source, "message": "m"})


def make_stats(*events):
    stats = Stats()
    for event in events:
        stats.add(event)
    return stats


def test_stats():
    stats = make_stats(ev("INFO", "a"), ev("ERROR", "b"), ev("CRITICAL", "b"),
                       ev("ERROR", "a", "2024-05-02T00:00:00Z"))
    assert stats.total == 4
    assert stats.by_source["b"] == 2
    assert stats.top_error_sources(1) == [("b", 2)]
    assert stats.first_ts.day == 1 and stats.last_ts.day == 2


def test_empty():
    stats = Stats()
    assert stats.total == 0 and stats.first_ts is None