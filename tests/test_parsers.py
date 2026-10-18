import pytest

from streamstats.errors import InvalidEventError, UnsupportedFormatError
from streamstats.parsers import SkipCounter, iter_events

CSV_HEADER = "timestamp,level,source,message\n"
CSV_ROW = "2024-05-01T12:00:00Z,INFO,db,hello\n"
JSON_LINE = '{"timestamp": "2024-05-01T12:00:00Z", "level": "INFO", "source": "db", "message": "hello"}\n'


def write(tmp_path, name, text, encoding="utf-8"):
    p = tmp_path / name
    p.write_text(text, encoding=encoding, newline="")
    return p


def test_csv_ok(tmp_path):
    p = write(tmp_path, "a.csv", CSV_HEADER + CSV_ROW * 2)
    events = list(iter_events(p, "csv"))
    assert len(events) == 2
    assert events[0].source == "db"
    assert events[0].level == "INFO"


def test_jsonl_ok(tmp_path):
    p = write(tmp_path, "a.jsonl", JSON_LINE * 2)
    events = list(iter_events(p, "jsonl"))
    assert len(events) == 2
    assert events[0].message == "hello"


def test_jsonl_blank_lines_ignored(tmp_path):
    p = write(tmp_path, "a.jsonl", "\n" + JSON_LINE + "   \n" + JSON_LINE)
    assert len(list(iter_events(p, "jsonl"))) == 2


def test_csv_multiline_field(tmp_path):
    text = CSV_HEADER + '2024-05-01T12:00:00Z,INFO,db,"строка 1\nстрока 2"\n'
    p = write(tmp_path, "a.csv", text)
    events = list(iter_events(p, "csv"))
    assert events[0].message == "строка 1\nстрока 2"


def test_csv_empty_file(tmp_path):
    assert list(iter_events(write(tmp_path, "a.csv", ""), "csv")) == []


def test_csv_header_only(tmp_path):
    assert list(iter_events(write(tmp_path, "a.csv", CSV_HEADER), "csv")) == []


def test_jsonl_empty_file(tmp_path):
    assert list(iter_events(write(tmp_path, "a.jsonl", ""), "jsonl")) == []


def test_csv_unicode(tmp_path):
    text = CSV_HEADER + "2024-05-01T12:00:00Z,ERROR,база,Ошибка 🔥\n"
    events = list(iter_events(write(tmp_path, "a.csv", text), "csv"))
    assert events[0].source == "база"
    assert events[0].message == "Ошибка 🔥"


def test_jsonl_unicode(tmp_path):
    line = '{"timestamp": "2024-05-01T12:00:00Z", "level": "ERROR", "source": "база", "message": "Ошибка 🔥"}\n'
    events = list(iter_events(write(tmp_path, "a.jsonl", line), "jsonl"))
    assert events[0].source == "база"
    assert events[0].message == "Ошибка 🔥"


def test_csv_with_bom(tmp_path):
    p = write(tmp_path, "a.csv", CSV_HEADER + CSV_ROW, encoding="utf-8-sig")
    assert len(list(iter_events(p, "csv"))) == 1


def test_jsonl_bad_line_strict(tmp_path):
    p = write(tmp_path, "a.jsonl", JSON_LINE + "мусор\n" + JSON_LINE)
    with pytest.raises(InvalidEventError) as info:
        list(iter_events(p, "jsonl"))
    assert info.value.line_no == 2
    assert "a.jsonl" in info.value.path


def test_csv_bad_row_strict(tmp_path):
    text = CSV_HEADER + CSV_ROW + "2024-05-01T12:00:00Z,FATAL,db,x\n"
    p = write(tmp_path, "a.csv", text)
    with pytest.raises(InvalidEventError) as info:
        list(iter_events(p, "csv"))
    assert info.value.line_no == 3  # заголовок = строка 1


def test_jsonl_not_an_object(tmp_path):
    p = write(tmp_path, "a.jsonl", "[1, 2]\n")
    with pytest.raises(InvalidEventError):
        list(iter_events(p, "jsonl"))


def test_jsonl_bad_timestamp(tmp_path):
    line = '{"timestamp": "вчера", "level": "INFO", "source": "db", "message": "m"}\n'
    with pytest.raises(InvalidEventError):
        list(iter_events(write(tmp_path, "a.jsonl", line), "jsonl"))


def test_jsonl_bad_line_skip(tmp_path, caplog):
    p = write(tmp_path, "a.jsonl", JSON_LINE + "мусор\n" + JSON_LINE)
    skipped = SkipCounter()
    events = list(iter_events(p, "jsonl", skip_invalid=True, skipped=skipped))
    assert len(events) == 2
    assert skipped.count == 1
    assert "пропущена" in caplog.text


def test_csv_bad_row_skip(tmp_path, caplog):
    text = CSV_HEADER + CSV_ROW + "2024-05-01T12:00:00Z,FATAL,db,x\n" + CSV_ROW
    p = write(tmp_path, "a.csv", text)
    skipped = SkipCounter()
    events = list(iter_events(p, "csv", skip_invalid=True, skipped=skipped))
    assert len(events) == 2
    assert skipped.count == 1
    assert "пропущена" in caplog.text


def test_csv_missing_columns_always_fails(tmp_path):
    p = write(tmp_path, "a.csv", "timestamp,level\n2024-05-01T12:00:00Z,INFO\n")
    with pytest.raises(InvalidEventError):
        list(iter_events(p, "csv", skip_invalid=True))


def test_unsupported_format(tmp_path):
    p = write(tmp_path, "a.xml", "<x/>")
    with pytest.raises(UnsupportedFormatError):
        list(iter_events(p, "xml"))