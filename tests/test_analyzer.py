from streamstats.analysis import Stats, filter_level, filter_source, filter_time
from streamstats.models import parse_event, parse_timestamp


def test_filter_level():
    events = [ev("INFO", "a"), ev("ERROR", "b")]
    assert [e.source for e in filter_level(events, {"ERROR"})] == ["b"]


def test_filter_source():
    events = [ev("INFO", "a"), ev("INFO", "b")]
    assert [e.source for e in filter_source(events, {"a"})] == ["a"]


def test_filter_time():
    events = [ev("INFO", "a", "2024-05-01T00:00:00Z"), ev("INFO", "b", "2024-05-03T00:00:00Z")]
    result = list(filter_time(events, since=parse_timestamp("2024-05-02T00:00:00Z")))
    assert [e.source for e in result] == ["b"]


def test_filters_are_lazy():
    def gen():
        yield ev("INFO", "a")
        raise AssertionError("прочитано больше, чем нужно")

    assert next(filter_level(gen(), {"INFO"})).source == "a"


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
